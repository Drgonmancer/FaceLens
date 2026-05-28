<template>
	<div class="register-container">
    <div class="bg-animation">
      <div class="particle" v-for="i in 20" :key="i"></div>
    </div>
		<div class="register_view">
			<el-form :model="registerForm" class="register_form">
				<div class="logo_area">
					<div class="logo_icon">
						<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
						</svg>
					</div>
					<div class="title_view">用户注册</div>
					<div class="subtitle">Create Your Account</div>
				</div>

				<div class="list_item">
					<el-input
						class="list_inp"
						v-model="registerForm.yonghuzhanghao"
						placeholder="请输入用户账号"
						prefix-icon="User"
					/>
				</div>

				<div class="list_item">
					<el-input
						class="list_inp"
						v-model="registerForm.mima"
						placeholder="请输入密码"
						type="password"
						prefix-icon="Lock"
						show-password
					/>
				</div>

				<div class="list_item">
					<el-input
						class="list_inp"
						v-model="registerForm.mima2"
						type="password"
						placeholder="请再次输入密码确认"
						prefix-icon="Lock"
						show-password
					/>
				</div>

				<div class="list_item">
					<el-input
						class="list_inp"
						v-model="registerForm.yonghuxingming"
						placeholder="请输入用户姓名"
						prefix-icon="Avatar"
					/>
				</div>

				<div class="list_item avatar_upload">
					<div class="upload_label">人脸照片（用于人脸识别登录）</div>
					<div class="upload_area">
						<uploads
							action="file/upload"
							tip="上传清晰正面照"
							:limit="1"
							:fileUrls="registerForm.touxiang ? registerForm.touxiang : ''"
							@change="touxiangUploadSuccess">
						</uploads>
					</div>
				</div>

				<div class="list_item">
					<el-input
						class="list_inp"
						v-model="registerForm.lianxidianhua"
						placeholder="请输入联系电话"
						prefix-icon="Phone"
					/>
				</div>

				<div class="list_item gender_select">
					<div class="select_label">性别</div>
					<el-radio-group v-model="registerForm.xingbie" class="gender_group">
						<el-radio value="男">男</el-radio>
						<el-radio value="女">女</el-radio>
					</el-radio-group>
				</div>

				<div class="list_btn">
					<el-button class="btn_register" type="primary" @click="handleRegister">
						<span>立即注册</span>
					</el-button>
					<div class="r-login" @click="close">已有账号？返回登录</div>
				</div>
			</el-form>
		</div>
	</div>
</template>
<script setup>
	import {
		ref,
		getCurrentInstance,
		nextTick,
		onUnmounted,
		onMounted,
	} from 'vue';
	const context = getCurrentInstance()?.appContext.config.globalProperties;
	const projectName = context?.$project.projectName

	const route = useRoute()
	const tableName = ref('yonghu')

	const registerForm = ref({
        xingbie: '',
	})
	const yonghuxingbieLists = ref([])
	const init=()=>{
		yonghuxingbieLists.value = "男,女".split(',')
	}

    const touxiangUploadSuccess=(fileUrls)=> {
        registerForm.value.touxiang = fileUrls;
    }

	const handleRegister = () => {
		let url = tableName.value +"/register";
		if((!registerForm.value.yonghuzhanghao)){
			context?.$toolUtil.message(`用户账号不能为空`,'error')
			return false
		}
		if((!registerForm.value.mima)){
			context?.$toolUtil.message(`密码不能为空`,'error')
			return false
		}
		if(registerForm.value.mima!=registerForm.value.mima2){
			context?.$toolUtil.message('两次密码输入不一致','error')
			return false
		}
		if((!registerForm.value.yonghuxingming)){
			context?.$toolUtil.message(`用户姓名不能为空`,'error')
			return false
		}
		if(registerForm.value.touxiang!=null){
			registerForm.value.touxiang = registerForm.value.touxiang.replace(new RegExp(context?.$config.url,"g"),"");
		}
		if(registerForm.value.lianxidianhua&&(!context?.$toolUtil.isMobile(registerForm.value.lianxidianhua))){
			context?.$toolUtil.message(`联系电话应输入手机格式`,'error')
			return false
		}
		if(!registerForm.value.touxiang){
			context?.$toolUtil.message('请上传人脸照片（用于人脸识别登录）','warning')
			return false
		}

		const loading = context?.$loading({
			lock: true,
			text: '正在注册账号...',
			background: 'rgba(0, 0, 0, 0.7)'
		})

		context?.$http({
			url:url,
			method:'post',
			data:registerForm.value
		}).then(res=>{
			const userId = res.data.data?.id
			if(userId && registerForm.value.touxiang){
				context?.$loading({
					lock: true,
					text: '正在注册人脸识别数据...',
					background: 'rgba(0, 0, 0, 0.7)'
				})
				context?.$http({
					url: 'face/register',
					method: 'post',
					data: {
						userid: userId,
						face: registerForm.value.touxiang,
						action: 'register'
					}
				}).then(faceRes => {
					loading.close()
					const faceCount = faceRes.data.data?.faceCount || 0
					context?.$toolUtil.message(`注册成功！人脸识别已启用（已录入${faceCount}张照片）`,'success', obj=>{
						context?.$router.push({
							path: "/login"
						});
					})
				}).catch(err => {
					loading.close()
					console.error('人脸注册失败:', err)
					context?.$toolUtil.message('账号注册成功，但人脸注册失败，您可以在个人中心重新录入','warning', obj=>{
						context?.$router.push({
							path: "/login"
						});
					})
				})
			} else {
				loading.close()
				context?.$toolUtil.message('注册成功','success', obj=>{
					context?.$router.push({
						path: "/login"
					});
				})
			}
		}).catch(err => {
			loading.close()
		})
	}

	const getUUID=()=> {
		return new Date().getTime();
	}

	const close = () => {
		context?.$router.push({
			path: "/login"
		});
	}
	init()
</script>

<style lang="scss" scoped>
.register-container {
	min-height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
	position: relative;
	overflow: hidden;

	.bg-animation {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 0;

		.particle {
			position: absolute;
			width: 4px;
			height: 4px;
			background: rgba(255,255,255,0.15);
			border-radius: 50%;
			animation: float 15s infinite ease-in-out;

			@for $i from 1 through 20 {
				&:nth-child(#{$i}) {
					left: random(100) * 1%;
					top: random(100) * 1%;
					animation-delay: $i * -0.7s;
					animation-duration: (random(20) + 10) * 1s;
					width: (random(5) + 2) * 1px;
					height: (random(5) + 2) * 1px;
				}
			}
		}
	}
}

@keyframes float {
	0%, 100% { transform: translateY(0) translateX(0); opacity: 0.3; }
	25% { transform: translateY(-30px) translateX(15px); opacity: 0.7; }
	50% { transform: translateY(-60px) translateX(-10px); opacity: 0.4; }
	75% { transform: translateY(-30px) translateX(20px); opacity: 0.6; }
}

.register_view {
	position: relative;
	z-index: 10;
	width: 450px;
	max-width: 90vw;
	max-height: 90vh;
	overflow-y: auto;

	.register_form {
		background: rgba(255, 255, 255, 0.95);
		border-radius: 20px;
		padding: 40px 35px;
		box-shadow:
			0 25px 60px rgba(0, 0, 0, 0.35),
			0 0 0 1px rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(20px);

		.logo_area {
			text-align: center;
			margin-bottom: 28px;

			.logo_icon {
				width: 60px;
				height: 60px;
				margin: 0 auto 12px;
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				border-radius: 16px;
				display: flex;
				align-items: center;
				justify-content: center;
				box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);

				svg {
					width: 30px;
					height: 30px;
					color: #fff;
				}
			}

			.title_view {
				font-size: 20px;
				font-weight: 700;
				color: #1a1a2e;
				margin-bottom: 5px;
				letter-spacing: 1px;
			}

			.subtitle {
				font-size: 12px;
				color: #888;
				font-weight: 400;
				letter-spacing: 2px;
				text-transform: uppercase;
			}
		}

		.list_item {
			margin-bottom: 14px;

			&.avatar_upload {
				display: block;

				.upload_label {
					font-size: 13px;
					color: #555;
					font-weight: 500;
					margin-bottom: 8px;
					padding-left: 2px;
				}

				.upload_area {
					background: #f7f8fc;
					border: 2px dashed #ddd;
					border-radius: 12px;
					padding: 15px;
					transition: all 0.3s;

					&:hover {
						border-color: #667eea;
						background: #fff;
					}

					:deep(.el-upload--picture-card),
					:deep(.el-upload-list__item) {
						border-radius: 10px;
						border-color: #e0e0e0;
						width: 120px;
						height: 120px;
					}
				}
			}

			&.gender_select {
				display: flex;
				align-items: center;
				gap: 12px;

				.select_label {
					font-size: 14px;
					color: #555;
					font-weight: 500;
					white-space: nowrap;
				}

				.gender_group {
					:deep(.el-radio__input.is-checked .el-radio__inner) {
						border-color: #667eea;
						background: #667eea;
					}
					:deep(.el-radio__input.is-checked + .el-radio__label) {
						color: #667eea;
					}
				}
			}

			:deep(.list_inp) {
				.el-input__wrapper {
					background: #f7f8fc;
					border: 2px solid transparent;
					border-radius: 12px;
					padding: 4px 14px;
					box-shadow: none;
					transition: all 0.3s ease;

					&:hover, &.is-focus {
						border-color: #667eea;
						background: #fff;
						box-shadow: 0 4px 15px rgba(102, 126, 234, 0.08);
					}

					.el-input__inner {
						font-size: 14px;
						line-height: 1.4;
					}

					.el-input__prefix .el-icon {
						color: #aaa;
						font-size: 16px;
					}
				}
			}
		}

		.list_btn {
			margin-top: 22px;
			text-align: center;

			.btn_register {
				width: 100%;
				height: 46px;
				border: none;
				border-radius: 12px;
				font-size: 16px;
				font-weight: 600;
				cursor: pointer;
				letter-spacing: 4px;
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: #fff;
				box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
				transition: all 0.3s ease;
				position: relative;
				overflow: hidden;

				&::before {
					content: '';
					position: absolute;
					top: 0;
					left: -100%;
					width: 100%;
					height: 100%;
					background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
					transition: left 0.5s;
				}

				&:hover {
					transform: translateY(-2px);
					box-shadow: 0 12px 30px rgba(102, 126, 234, 0.45);
				}

				&:hover::before {
					left: 100%;
				}
			}

			.r-login {
				margin-top: 14px;
				cursor: pointer;
				color: #888;
				font-size: 13px;
				transition: color 0.3s;

				&:hover {
					color: #667eea;
				}
			}
		}
	}
}
</style>
