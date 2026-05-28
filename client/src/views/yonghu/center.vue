
<template>
	<div>
		<div class="app-contain">
			<el-form class="userinfo_form" ref="userinfoFormRef" :model="form" label-width="$template2.back.add.form.base.labelWidth">
				<el-row>
					<el-col :span="24">
						<el-form-item label="用户账号" prop="yonghuzhanghao">
							<el-input class="list_inp" v-model="user.yonghuzhanghao" readonly placeholder="用户账号" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="用户姓名" prop="yonghuxingming">
							<el-input class="list_inp" v-model="user.yonghuxingming"  placeholder="用户姓名" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="头像" prop="touxiang">
							<uploads
								action="file/upload" 
								tip="请上传头像" 
								:limit="3" 
								style="width: 100%;text-align: left;"
								:fileUrls="user.touxiang?user.touxiang:''" 
								@change="yonghutouxiangUploadSuccess">
							</uploads>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="联系电话" prop="lianxidianhua">
							<el-input class="list_inp" v-model="user.lianxidianhua"  placeholder="联系电话" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="性别" prop="xingbie">
							<el-select
								class="list_sel"
								v-model="user.xingbie"
								placeholder="请选择性别"
								>
								<el-option v-for="item in yonghuxingbieLists" :label="item" :value="item"></el-option>
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<div class="face-management-section">
							<div class="section-title">
								<span>🔐 人脸识别管理</span>
								<el-tag :type="faceStatus.registered ? 'success' : 'warning'" size="small">
									{{ faceStatus.registered ? '已启用' : '未启用' }}
								</el-tag>
							</div>
							<div class="face-info">
								<p>已录入人脸照片：<strong>{{ faceStatus.faceCount }}</strong> 张</p>
								<p class="tip">提示：启用后可使用"面容ID"方式快速登录</p>
							</div>
							<div class="face-actions">
								<el-button type="primary" @click="handleFaceRegister">
									{{ faceStatus.registered ? '重新录入手脸' : '立即启用人脸登录' }}
								</el-button>
								<el-button v-if="faceStatus.registered && faceStatus.faceCount > 0"
										   type="danger"
										   plain
										   @click="handleDeleteFaces">
									清除所有人脸数据
								</el-button>
							</div>
						</div>
					</el-col>
					<span class="userinfo_form_btn_box">
						<el-button class='userinfo_confirm' type="primary" @click="onSubmit">保存</el-button>
					</span>
				</el-row>
			</el-form>
		</div>
	</div>
</template>

<script setup>
	import { isNumber,isIntNumer,isEmail,isMobile,isPhone,isURL,checkIdCard } from "@/utils/toolUtil";
	import {
		reactive,
		ref,
		getCurrentInstance
	} from 'vue'
	const context = getCurrentInstance()?.appContext.config.globalProperties;
	const tableName = ref('yonghu')
	const user = ref({})
	const yonghuxingbieLists = ref([])
	const faceStatus = ref({
		registered: false,
		faceCount: 0
	})
	const init = () => {
		yonghuxingbieLists.value = "男,女".split(',')
	}

	const checkFaceStatus = () => {
		if(!user.value.id) return
		context?.$http({
			url: 'face/register',
			method: 'post',
			data: {
				userid: user.value.id,
				action: 'check'
			}
		}).then(res => {
			if(res.data && res.data.data) {
				faceStatus.value = {
					registered: res.data.data.registered === 1,
					faceCount: res.data.data.faceCount || 0
				}
			}
		}).catch(err => {
			console.error('查询人脸状态失败:', err)
		})
	}

	const handleFaceRegister = () => {
		const input = document.createElement('input')
		input.type = 'file'
		input.accept = 'image/*'
		input.onchange = (e) => {
			const file = e.target.files[0]
			if(!file) return

			const reader = new FileReader()
			reader.onload = (event) => {
				const base64 = event.target.result
				const loading = context?.$loading({
					lock: true,
					text: '正在处理人脸数据...',
					background: 'rgba(0, 0, 0, 0.7)'
				})

				context?.$http({
					url: 'face/register',
					method: 'post',
					data: {
						userid: user.value.id,
						face: base64,
						action: 'register'
					}
				}).then(res => {
					loading.close()
					if(res.data.code === 200 || res.data.code === 0) {
						const count = res.data.data?.faceCount || 0
						context?.$toolUtil.message(`人脸注册成功！已录入${count}张照片`,'success')
						checkFaceStatus()
					} else {
						context?.$toolUtil.message(res.data.msg || '注册失败','error')
					}
				}).catch(err => {
					loading.close()
					console.error('人脸注册失败:', err)
					context?.$toolUtil.message('人脸注册失败，请重试','error')
				})
			}
			reader.readAsDataURL(file)
		}
		input.click()
	}

	const handleDeleteFaces = () => {
		context?.$confirm('确定要清除所有已录入的人脸数据吗？清除后将无法使用面容ID登录', '提示', {
			confirmButtonText: '确定清除',
			cancelText: '取消',
			type: 'warning'
		}).then(() => {
			const loading = context?.$loading({
				lock: true,
				text: '正在清除人脸数据...',
				background: 'rgba(0, 0, 0, 0.7)'
			})

			context?.$http({
				url: 'face/register',
				method: 'post',
				data: {
					userid: user.value.id,
					action: 'delete_all'
				}
			}).then(res => {
				loading.close()
				context?.$toolUtil.message('人脸数据已清除','success')
				checkFaceStatus()
			}).catch(err => {
				loading.close()
				context?.$toolUtil.message('清除失败，请重试','error')
			})
		}).catch(() => {})
	}
	const yonghutouxiangUploadSuccess=(fileUrls)=> {
	    user.value.touxiang = fileUrls;
	}
	const onSubmit = () => {
		if((!user.value.yonghuzhanghao)){
			context?.$toolUtil.message(`用户账号不能为空`,'error')
			return false
		}
		if((!user.value.mima)){
			context?.$toolUtil.message(`密码不能为空`,'error')
			return false
		}
		if((!user.value.yonghuxingming)){
			context?.$toolUtil.message(`用户姓名不能为空`,'error')
			return false
		}
		if(user.value.touxiang!=null){
			user.value.touxiang = user.value.touxiang.replace(new RegExp(context?.$config.url,"g"),"");
		}
		if((user.value.lianxidianhua)&&(!context?.$toolUtil.isMobile(user.value.lianxidianhua))){
			context?.$toolUtil.message(`联系电话应输入手机格式`,'error')
			return false
		}
		context?.$http({
			url: `${tableName.value}/update`,
			method: 'post',
			data: user.value
		}).then(res => {
			context?.$toolUtil.message('修改成功','success')
		})

	}
	const getInfo = () => {
		context?.$http({
			url: `${tableName.value}/session`,
			method: 'get'
		}).then(res => {
			user.value = res.data.data
			init()
			checkFaceStatus()
		})
	}
	getInfo()
</script>

<style lang="scss" scoped>
	// 表单
	.userinfo_form {
		border: 1px solid rgba(254, 182, 203, 0.5);
		border-radius: 0px;
		padding: 40px 30px;
		margin: 0;
		background: #fff;
		// form item
		:deep(.el-form-item) {
			margin: 0 150px 20px 0;
			background: none;
			display: flex;
			// 内容盒子
			.el-form-item__content{
				display: flex;
				width: calc(100% - 120px);
				justify-content: flex-start;
				align-items: center;
				flex-wrap: wrap;
			}
			// 输入框
			.list_inp {
				border: 0px solid rgba(255, 255, 255, 0.25);
				border-radius: 0px;
				padding: 0 10px;
				color: #666;
				background: rgba(0, 0, 0, 0.1);
				width: auto;
				line-height: 36px;
				box-sizing: border-box;
				height: 36px;
				//去掉默认样式
				.el-input__wrapper{
					border: none;
					box-shadow: none;
					background: none;
					border-radius: 0;
					height: 100%;
					padding: 0;
				}
				.is-focus {
					box-shadow: none !important;
				}
			}
			//下拉框样式
			.list_sel {
				border: 1px solid rgba(255, 255, 255, 0.25);
				border-radius: 0px;
				padding: 0 10px;
				color: #666;
				background: rgba(0, 0, 0, 0.1);
				width: auto;
				line-height: 36px;
				box-sizing: border-box;
				//去掉默认样式
				.select-trigger{
					height: 100%;
					.el-input{
						height: 100%;
						.el-input__wrapper{
							border: none;
							box-shadow: none;
							background: none;
							border-radius: 0;
							height: 100%;
						}
						.is-focus {
							box-shadow: none !important;
						}
					}
				}
			}
			//图片上传样式
			.el-upload-list  {
				//提示语
				.el-upload__tip {
					margin: 7px 0 0;
					color: #999;
					display: flex;
					font-size: 14px;
					justify-content: flex-start;
					align-items: center;
				}
				//外部盒子
				.el-upload--picture-card {
					border: 1px solid rgba(255, 255, 255, 0.25);
					cursor: pointer;
					border-radius: 0px;
					background: rgba(0, 0, 0, 0.1);
					width: 120px;
					line-height: 70px;
					text-align: center;
					height: 60px;
					//图标
					.el-icon{
						color: #999;
						font-size: 26px;
					}
				}
				.el-upload-list__item {
					border: 1px solid rgba(255, 255, 255, 0.25);
					cursor: pointer;
					border-radius: 0px;
					background: rgba(0, 0, 0, 0.1);
					width: 120px;
					line-height: 70px;
					text-align: center;
					height: 60px;
				}
			}

		}
		// 按钮盒子
		.userinfo_form_btn_box {
			display: flex;
			width: 100%;
			justify-content: center;
			align-items: center;
			// 确定按钮
			.userinfo_confirm {
				border: 1px solid #357ebd;
				cursor: pointer;
				border-radius: 3px;
				padding: 0 24px;
				margin: 0 20px 0 0;
				outline: none;
				color: #fff;
				background: rgba(66, 139, 202, 0.55);
				width: auto;
				font-size: 14px;
				min-width: 100px;
				height: 36px;
			}
			// 确定按钮-悬浮
			.userinfo_confirm:hover {
			}
		}

		// 人脸管理区域
		.face-management-section {
			margin: 25px 150px 20px 0;
			padding: 20px;
			background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
			border: 2px solid #e0e6ed;
			border-radius: 12px;

			.section-title {
				display: flex;
				align-items: center;
				justify-content: space-between;
				margin-bottom: 15px;
				padding-bottom: 12px;
				border-bottom: 2px solid #d0d7de;

				span {
					font-size: 16px;
					font-weight: 600;
					color: #2c3e50;
				}
			}

			.face-info {
				margin-bottom: 18px;

				p {
					margin: 8px 0;
					font-size: 14px;
					color: #555;

					strong {
						color: #667eea;
						font-size: 18px;
						font-weight: 700;
					}

					&.tip {
						font-size: 12px;
						color: #999;
						margin-top: 10px;
					}
				}
			}

			.face-actions {
				display: flex;
				gap: 12px;
				flex-wrap: wrap;

				.el-button {
					padding: 10px 20px;
					font-size: 14px;
					font-weight: 500;
					border-radius: 8px;
					transition: all 0.3s ease;

					&:hover {
						transform: translateY(-2px);
						box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
					}
				}
			}
		}
	}
</style>
