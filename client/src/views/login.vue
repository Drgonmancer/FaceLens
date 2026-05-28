<template>
	<div class="login-container">
    <div class="bg-animation">
      <div class="particle" v-for="i in 20" :key="i"></div>
    </div>
		<div class="login_view">
			<el-form :model="loginForm" class="login_form">
				<div class="logo_area">
					<div class="logo_icon">
						<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
						</svg>
					</div>
					<div class="title_view">基于OpenCV和Python的人脸识别系统</div>
					<div class="subtitle">Face Recognition System</div>
				</div>

				<el-tabs v-model="loginType" class="login_tabs" stretch>
					<el-tab-pane label="账号登录" name="1">
						<div class="list_item">
							<div class="input_icon">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
							</div>
							<input class="list_inp" v-model="loginForm.username" placeholder="请输入账号" />
						</div>
						<div class="list_item">
							<div class="input_icon">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>
							</div>
							<input class="list_inp" v-model="loginForm.password" type="password" placeholder="请输入密码" @keydown.enter.native="handleLogin" />
						</div>
					</el-tab-pane>
					<el-tab-pane label="面容ID登录" name="2">
						<div class="face_login_tips">
							<div class="face_scan_icon">
								<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
									<path d="M12 2a10 10 0 1010 10A10 10 0 0012 2zm0 18a8 8 0 118-8 8 8 0 01-8 8z"/>
									<path d="M12 6a6 6 0 00-6 6h2a4 4 0 014-4z"/>
									<circle cx="12" cy="12" r="2"/>
								</svg>
							</div>
							<p>点击下方按钮进行人脸扫描认证</p>
						</div>
					</el-tab-pane>
				</el-tabs>

				<div class="list_type" v-if="userList.length>1">
					<div class="select_label">用户类型</div>
				  <el-select v-model="loginForm.role" placeholder="请选择用户类型">
				    <el-option v-for="(item,index) in userList" :label="item.roleName" :value="item.roleName"></el-option>
				  </el-select>
				</div>

				<div class="btn_view">
					<el-button class="btn_login" v-if="loginType=='1'" @click="handleLogin">
						<span>登 录</span>
					</el-button>
					<el-button class="btn_face" v-if="loginType=='2'" @click="handleFaceLogin">
						<span>开始人脸认证</span>
					</el-button>
				</div>

				<div class="footer_tips">
					<p>安全提示：本系统采用OpenCV本地算法进行人脸识别</p>
				</div>
			</el-form>
		</div>
		<Vcode :show="isShow" @success="success" @close="close" @fail='fail'></Vcode>
		<imgAdd ref="faceImg" @imgChange="imgChange"></imgAdd>
	</div>
</template>
<script setup>
	import {
		ref,
		getCurrentInstance,
		nextTick,
		onMounted,
		onUnmounted,
	} from "vue";
	const userList = ref([])
	const menus = ref([])
	const loginForm = ref({
		role: '',
		username: '',
		password: ''
	})
	const tableName = ref('')
	const loginType = ref('1')
	const context = getCurrentInstance()?.appContext.config.globalProperties;
	import imgAdd from '@/components/common/img'
	import { ElLoading } from 'element-plus'
	const faceImg = ref(null)

	const handleFaceLogin=()=>{
		if (userList.value.length > 1) {
			if (!loginForm.value.role) {
				context?.$toolUtil.message('请选择角色', 'error')
				return;
			}
			for (let i = 0; i < menus.value.length; i++) {
				if (menus.value[i].roleName == loginForm.value.role) {
					tableName.value = menus.value[i].tableName;
				}
			}
		} else {
			tableName.value = userList.value[0].tableName;
			loginForm.value.role = userList.value[0].roleName;
		}
		nextTick(()=>{
			faceImg.value.onTake()
		})
	}

	const imgChange=(e)=>{
		const loading = ElLoading.service({
		    lock: true,
		    text: '正在进行人脸识别...',
		    background: 'rgba(0, 0, 0, 0.7)',
		})
		context?.$http({
			url: `${tableName.value}/faceLogin?face=${e}`,
			method: 'post'
		}).then(res => {
			if (loading) loading.close()
			
			console.log('人脸登录响应:', res.data)
			
			if (res.data.code !== 0 && res.data.code !== 200) {
				const errorMsg = res.data.msg || '人脸识别失败'
				console.error('人脸登录失败:', errorMsg)
				context?.$toolUtil.message(errorMsg, 'error')
				return
			}
			
			if (!res.data.token) {
				console.error('未获取到token:', res.data)
				context?.$toolUtil.message('人脸识别成功但未获取到登录凭证，请重试', 'error')
				return
			}

			context?.$toolUtil.storageSet("Token", res.data.token);
			context?.$toolUtil.storageSet("role", loginForm.value.role);
			context?.$toolUtil.storageSet("sessionTable", tableName.value);
			context?.$toolUtil.storageSet("adminName", loginForm.value.username);
			context?.$router.push('/')
		},err=>{
			if (loading) loading.close()
			console.error('人脸登录请求异常:', err)
			context?.$toolUtil.message('人脸识别请求失败，请检查网络连接', 'error')
		})
	}

	const handleLogin = () => {
		if (!loginForm.value.username) {
			context?.$toolUtil.message('请输入用户名', 'error')
			return;
		}
		if (!loginForm.value.password) {
			context?.$toolUtil.message('请输入密码', 'error')
			return;
		}
		if (userList.value.length > 1) {
			if (!loginForm.value.role) {
				context?.$toolUtil.message('请选择角色', 'error')
				return;
			}
			for (let i = 0; i < menus.value.length; i++) {
				if (menus.value[i].roleName == loginForm.value.role) {
					tableName.value = menus.value[i].tableName;
				}
			}
		} else {
			tableName.value = userList.value[0].tableName;
			loginForm.value.role = userList.value[0].roleName;
		}
		login()
	}

	const login = () => {
		context?.$http({
			url: `${tableName.value}/login?username=${loginForm.value.username}&password=${loginForm.value.password}`,
			method: 'post'
		}).then(res => {
			context?.$toolUtil.storageSet("Token", res.data.token);
			context?.$toolUtil.storageSet("role", loginForm.value.role);
			context?.$toolUtil.storageSet("sessionTable", tableName.value);
			context?.$toolUtil.storageSet("adminName", loginForm.value.username);
			context?.$router.push('/')
		}, err => {
		})
	}

	const getMenu=()=> {
      let params = {
        page: 1,
        limit: 1,
        sort: 'id',
      }
      context?.$http({
        url: "menu/list",
        method: "get",
        params: params
      }).then(res => {
          menus.value = JSON.parse(res.data.data.list[0].menujson)
          for (let i = 0; i < menus.value.length; i++) {
            if (menus.value[i].hasBackLogin=='是') {
              userList.value.push(menus.value[i])
            }
          }
			loginForm.value.role = userList.value[0].roleName
          context?.$toolUtil.storageSet("menus", JSON.stringify(menus.value));
      })
    }

	const init = () => {
		getMenu();
	}

	onMounted(()=>{
		init()
	})
</script>

<style lang="scss" scoped>
.login-container {
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

.login_view {
	position: relative;
	z-index: 10;
	width: 420px;
	max-width: 90vw;

	.login_form {
		background: rgba(255, 255, 255, 0.95);
		border-radius: 20px;
		padding: 40px 35px;
		box-shadow:
			0 25px 60px rgba(0, 0, 0, 0.35),
			0 0 0 1px rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(20px);

		.logo_area {
			text-align: center;
			margin-bottom: 30px;

			.logo_icon {
				width: 64px;
				height: 64px;
				margin: 0 auto 15px;
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				border-radius: 16px;
				display: flex;
				align-items: center;
				justify-content: center;
				box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);

				svg {
					width: 32px;
					height: 32px;
					color: #fff;
				}
			}

			.title_view {
				font-size: 20px;
				font-weight: 700;
				color: #1a1a2e;
				margin-bottom: 6px;
				letter-spacing: 1px;
			}

			.subtitle {
				font-size: 13px;
				color: #888;
				font-weight: 400;
				letter-spacing: 2px;
				text-transform: uppercase;
			}
		}

		.login_tabs {
			margin-bottom: 20px;

			:deep(.el-tabs__header) {
				margin-bottom: 20px;
			}

			:deep(.el-tabs__nav-wrap::after) {
				height: 1px;
				background: #eee;
			}

			:deep(.el-tabs__item) {
				font-size: 14px;
				font-weight: 600;
				color: #999;

				&.is-active {
					color: #667eea;
				}
			}

			:deep(.el-tabs__active-bar) {
				background-color: #667eea;
				height: 3px;
				border-radius: 2px;
			}
		}

		.list_item {
			display: flex;
			align-items: center;
			background: #f7f8fc;
			border: 2px solid transparent;
			border-radius: 12px;
			padding: 0 16px;
			margin-bottom: 14px;
			transition: all 0.3s ease;

			&:hover, &:focus-within {
				border-color: #667eea;
				background: #fff;
				box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
			}

			.input_icon {
				flex-shrink: 0;
				width: 36px;
				display: flex;
				align-items: center;
				justify-content: center;
				color: #aaa;

				svg {
					width: 18px;
					height: 18px;
				}
			}

			.list_inp {
				border: none;
				outline: none;
				background: transparent;
				flex: 1;
				padding: 14px 8px;
				font-size: 14px;
				color: #333;
				line-height: 1.4;

				&::placeholder {
					color: #bbb;
				}
			}
		}

		.face_login_tips {
			text-align: center;
			padding: 25px 0 10px;

			.face_scan_icon {
				margin-bottom: 12px;
				animation: pulse 2s ease-in-out infinite;

				svg {
					color: #667eea;
				}
			}

			p {
				font-size: 13px;
				color: #888;
			}
		}

		@keyframes pulse {
			0%, 100% { transform: scale(1); opacity: 1; }
			50% { transform: scale(1.08); opacity: 0.8; }
		}

		.list_type {
			display: flex;
			align-items: center;
			margin-bottom: 18px;
			gap: 12px;

			.select_label {
				font-size: 14px;
				color: #555;
				font-weight: 500;
				white-space: nowrap;
			}

			:deep(.el-select) {
				flex: 1;

				.select-trigger {
					.el-input {
						.el-input__wrapper {
							background: #f7f8fc;
							border-radius: 10px;
							box-shadow: none;
							border: 2px solid transparent;
							padding: 4px 12px;
							transition: all 0.3s;

							&:hover, &.is-focus {
								border-color: #667eea;
								background: #fff;
							}
						}
					}
				}
			}
		}

		.btn_view {
			margin-top: 10px;

			.btn_login, .btn_face {
				width: 100%;
				height: 48px;
				border: none;
				border-radius: 12px;
				font-size: 16px;
				font-weight: 600;
				cursor: pointer;
				letter-spacing: 3px;
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

				&:hover::before {
					left: 100%;
				}
			}

			.btn_login {
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: #fff;
				box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);

				&:hover {
					transform: translateY(-2px);
					box-shadow: 0 12px 30px rgba(102, 126, 234, 0.5);
				}
			}

			.btn_face {
				background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
				color: #fff;
				box-shadow: 0 8px 25px rgba(56, 239, 125, 0.3);

				&:hover {
					transform: translateY(-2px);
					box-shadow: 0 12px 30px rgba(56, 239, 125, 0.45);
				}
			}
		}

		.footer_tips {
			text-align: center;
			margin-top: 20px;
			padding-top: 18px;
			border-top: 1px solid #f0f0f0;

			p {
				font-size: 11px;
				color: #bbb;
			}
		}
	}
}
</style>
