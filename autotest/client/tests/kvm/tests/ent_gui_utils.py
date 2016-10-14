import sys, os, subprocess, commands, string, re, random, pexpect, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
LDTP_SERVER_ADDR = commands.getoutput("grep 'LDTP_SERVER_ADDR' /etc/profile | cut -d '=' -f 2")
if not LDTP_SERVER_ADDR == "":
	os.environ["LDTP_SERVER_ADDR"] = LDTP_SERVER_ADDR
import ldtp, ooldtp

class ent_gui_utils:
	# ========================================================
	# 	1. LDTP GUI test special functions
	# ========================================================
	def open_subscription_manager(self, session):
		self.set_os_release(session)
		if self.get_os_release().split('.')[0] == "5":
			ldtp.launchapp2("subscription-manager-gui")
		else:
			ldtp.launchapp("subscription-manager-gui")
		self.check_window_exist("main-window")
		logging.info("open_subscription_manager")

	def open_firstboot(self, session):
		self.set_os_release(session)
		ldtp.launchapp("firstboot")
		self.check_window_exist('firstboot-main-window')
		logging.info("open_firstboot")

	def close_firstboot(self, session):
		cmd = "killall -9 firstboot"
		(ret, output) = eu().runcmd(session, cmd, "close firstboot-gui")
		if ret == 0:
			logging.info("It's successful to close firstboot-gui.")

	def register_in_gui(self, username, password):
		self.click_register_button()
		self.click_dialog_next_button()
		self.input_username(username)
		self.input_password(password)
		self.click_dialog_register_button()
		self.click_dialog_cancle_button()
		
	def register_and_autosubscribe_in_gui(self, username, password):
		self.click_register_button()
		self.click_dialog_next_button()
		self.input_username(username)
		self.input_password(password)
		self.click_dialog_register_button()
		self.click_dialog_subscribe_button()
		time.sleep(20)

	def click_register_button(self):
		self.click_button("main-window", "register-button")
		self.check_window_exist("register-dialog")
		logging.info("click_register_button")

	def click_autoattach_button(self):
		self.click_button("main-window", "auto-subscribe-button")
		self.check_window_exist("register-dialog")
		self.wait_until_button_enabled("register-dialog", "dialog-register-button")
		logging.info("click_autoattach_button")

	def click_attach_button(self):
		self.click_button("register-dialog", "dialog-register-button")
		self.check_window_closed("register-dialog")
		time.sleep(20)
		logging.info("click_attach_button")

	def click_remove_subscriptions_button(self):
		self.click_button("main-window", "remove-subscriptions-button")
		self.check_window_exist("question-dialog")
		self.click_button("question-dialog", "yes-button")
		self.check_window_closed("question-dialog")
		logging.info("click_remove_subscriptions_button")

	def click_ImportCertificate_button(self):
		self.click_menu("main-window", "ImportCertificate-menu")
		self.check_window_exist("import-cert-dialog")
		logging.info("click_ImportCertificate_menu")

	def click_Certificate_Location(self):
		if self.get_os_release() == "6.4":
			return
		else:
			self.click_button("import-cert-dialog", "type-pem-name-button")
			time.sleep(30)
			if ldtp.guiexist(self.get_window("import-cert-dialog"), self.get_text("location-text")):
				logging.info("click_Certificate_Location")

	def click_type_file_name_button(self):
		if ldtp.guiexist(self.get_window("import-certificate-dialog"), self.get_text("location-text")) == 1:
			return
		else:
			self.click_button("import-certificate-dialog", "type-file-name-button")
			ldtp.waittillguiexist(self.get_window("import-certificate-dialog"), self.get_text("location-text"))
			# self.check_element_exist("import-certificate-dialog", "location-text")
			logging.info("click_type_file_name_button")
			
	def click_import_cert_button(self):
		self.click_button("import-cert-dialog", "import-file-button")
		self.check_window_exist("error-cert-dialog")
		logging.info("click import cert button")
		
	def close_error_cert_dialog(self):
		self.click_button("error-cert-dialog", "ok-button")
		time.sleep(10)
		if not self.check_object_exist("error-cert-dialog", "error-cert-dialog"):
			logging.info("It's successful to close import-cert-error-dialog and it's successful to check importing wrong cert")
	
	def select_org_and_register(self):
		self.check_window_exist("register-dialog")
		ldtp.selectlastrow('register-dialog', 'orgs-view-table')
		logging.info("select ACME_Corporation org")
		self.click_button('register-dialog', 'dialog-register-button')
		logging.info("It's successful register, please check /etc/pki/consumer")
		
	def click_open_file_button(self):
		self.click_button("import-certificate-dialog", "open-file-button")
		self.check_window_exist("information-dialog")
		logging.info("click_open_file_button")

	def click_dialog_next_button(self):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			self.click_button("register-dialog", "dialog-register-button")
			self.check_window_exist("register-dialog")
			logging.info("click_dialog_next_button")

	def click_configure_proxy_button(self):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			self.click_button("register-dialog", "configure-proxy-button")
			self.check_window_exist("proxy-configuration-dialog")
			logging.info("click_configure_proxy_button")

	def click_dialog_register_button(self):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			self.click_button("register-dialog", "dialog-register-button")
			self.wait_until_button_enabled("register-dialog", "dialog-register-button")
		else:
			self.click_button("register-dialog", "dialog-register-button")
			self.check_window_exist("subscribe-dialog")
		logging.info("click_dialog_register_button")

	def click_dialog_register_button_without_autoattach(self):
		self.click_button("register-dialog", "dialog-register-button")
		self.check_window_closed("register-dialog")
		logging.info("click_dialog_register_button_without_autoattach")
	
	def click_dialog_register_for_account_without_org_access(self):
		self.click_button('register-dialog', 'dialog-register-button')
		time.sleep(10)
		if self.check_object_exist('error-dialog', 'error-user-label'):
			return 1
		else:
			return 0

	def click_dialog_subscribe_button(self):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			self.click_button("register-dialog", "dialog-register-button")
			self.check_window_closed("register-dialog")
		else:
			self.click_button("subscribe-dialog", 'dialog-subscribe-button')
			self.check_window_closed("subscribe-dialog")
		logging.info("click_dialog_subscribe_button")

	def click_dialog_cancle_button(self):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			self.click_button("register-dialog", "dialog-cancle-button")
			self.check_window_closed("register-dialog")
		else:
			self.click_button("subscribe-dialog", 'dialog-cancle-button')
			self.check_window_closed("subscribe-dialog")
		logging.info("click_dialog_cancle_button")

	def click_proxy_close_button(self):
		self.click_button("proxy-configuration-dialog", "proxy-close-button")
		self.check_window_closed("proxy-configuration-dialog")
		logging.info("click_proxy_close_button")

	def click_close_button(self):
		self.click_button("system-preferences-dialog", "close-button")
		self.check_window_closed("system-preferences-dialog")
		logging.info("click_close_button")

	def click_filter_close_button(self):
		self.click_button("filter-options-window", "close-button")
		self.check_window_closed("filter-options-window")
		logging.info("click_filter_close_button")

	def click_all_available_subscriptions_tab(self):
		self.click_tab('all-available-subscriptions')
		ldtp.wait(5)
		logging.info("click_all_available_subscriptions_tab")

	def click_update_button(self):
		self.click_button("main-window", "update-button")
		self.check_window_exist("search-dialog")
		self.check_window_closed("search-dialog")
		logging.info("click_update_button")

	def click_filters_button(self):
		self.click_button("main-window", "filters-button")
		self.check_window_exist("filter-options-window")
		logging.info("click_filters_button")

	def click_my_subscriptions_tab(self):
		self.click_tab('my-subscriptions')
		ldtp.wait(5)
		logging.info("click_my_subscriptions_tab")

	def click_my_installed_products_tab(self):
		self.click_tab('my-installed-software')
		ldtp.wait(5)
		logging.info("click_my_installed_products_tab")

	def input_location(self, location):
		self.input_text("import-cert-dialog", "location-text", location)
		ldtp.wait(5)
		logging.info("input_location")

	def input_username(self, username):
		self.input_text("register-dialog", "login-text", username)
		logging.info("input_username")

	def input_password(self, password):
		self.input_text("register-dialog", "password-text", password)
		logging.info("input_password")

	def input_HTTP_proxy(self, proxy):
		self.input_text("proxy-configuration-dialog", "proxy-location-text", proxy)
		logging.info("input_HTTP_proxy")


	def get_all_subscription_table_row_count(self):
		return self.get_table_row_count("main-window", 'all-subscription-table')

	def get_my_subscriptions_table_row_count(self):
		return self.get_table_row_count("main-window", 'my-subscription-table')

	def click_view_system_facts_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "system-menu")
			self.click_menu("main-window", "viewsystemfacts-menu")
			self.check_window_exist("system-facts-dialog")
			logging.info("click_view_system_facts_menu")

	def click_import_cert_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "system-menu")
			self.click_menu("main-window", "importcert-menu")
			self.check_window_exist("import-certificate-dialog")
			logging.info("click_import_cert_menu")

	def click_preferences_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "system-menu")
			self.click_menu("main-window", "preferences-menu")
			self.check_window_exist("system-preferences-dialog")
			time.sleep(20)
			logging.info("click_preferences_menu")

	def click_gettingstarted_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "help-menu")
			self.click_menu("main-window", "gettingstarted-menu")
			self.check_window_exist("subscription-manager-manual-window")
			logging.info("click_gettingstarted_menu")

	def click_onlinedocumentation_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "help-menu")
			self.click_menu("main-window", "onlinedocumentation-menu")
			self.check_window_exist("onlinedocumentation-window")
			logging.info("click_onlinedocumentation_menu")

	def click_about_menu(self):
		if self.get_os_release() == "6.4":
			self.click_menu("main-window", "help-menu")
			self.click_menu("main-window", "about-menu")
			self.check_window_exist("about-subscription-manager-dialog")
			logging.info("click_about_menu")


	def click_unregister_menu(self):
		self.click_menu("main-window", "unregister-menu")
		self.check_window_exist("question-dialog")
		self.click_button("question-dialog", "yes-button")
		self.check_window_closed("question-dialog")
		logging.info("click_unregister_menu")

	def click_facts_view_tree(self, branch):
		if self.get_os_release() == "6.4":
			ldtp.doubleclickrow(self.get_window("system-facts-dialog"), self.get_table("facts-view-table"), branch)
			ldtp.wait(5)
			logging.info("click_facts_view_tree")

	def check_manual_attach_checkbox(self):
		self.check_checkbox("register-dialog", "manual-attach-checkbox")
		logging.info("check_manual_attach_checkbox")

	def uncheck_manual_attach_checkbox(self):
		self.uncheck_checkbox("register-dialog", "manual-attach-checkbox")
		logging.info("uncheck_manual_attach_checkbox")

	def check_HTTP_proxy_checkbox(self):
		self.check_checkbox("proxy-configuration-dialog", "proxy-checkbox")
		logging.info("check_HTTP_proxy_checkbox")


	def get_my_subscriptions_table_my_subscriptions(self):
		for row in range(self.get_my_subscriptions_table_row_count()):
			return self.get_table_cell("main-window", 'my-subscription-table', row , 0)

	def check_content_in_all_subscription_table(self, content):
		for row in range(self.get_all_subscription_table_row_count()):
			if self.get_table_cell("main-window", 'all-subscription-table', row , 0) == content:
				logging.info("%s is listed in all-subscription-table" % content)
				return True
		return False

	def check_content_in_my_installed_products_table(self, content):
		for row in range(self.get_all_subscription_table_row_count()):
			if self.get_table_cell("main-window", 'installed-product-table', row , 0) == content:
				logging.info("%s is listed in my_installed_products_table" % content)
				return True
		return False

	def check_content_in_my_subscriptions_table(self, content):
		for row in range(self.get_all_subscription_table_row_count()):
			if self.get_table_cell("main-window", 'my-subscription-table', row , 0) == content:
				logging.info("%s is listed in my_subscriptions_table" % content)
				return True
		return False

	def check_list_item_selected(self, window, list, item):
# 		for row in range(self.get_all_subscription_table_row_count()):
# 			if self.get_table_cell("main-window", 'my-subscription-table', row , 0) == content:
# 				logging.info("%s is listed in my_subscriptions_table" % content)
# 				return True
 		return False

	def check_item_in_list(self, window, list, item):
# 		for row in range(self.get_all_subscription_table_row_count()):
# 			if self.get_table_cell("main-window", 'my-subscription-table', row , 0) == content:
# 				logging.info("%s is listed in my_subscriptions_table" % content)
# 				return True
 		return False

	def check_org_displayed_in_facts(self, session, username, password):
		cmd = "subscription-manager orgs --user=%s --password=%s | grep Key" % (username, password)
		(ret, output) = eu().runcmd(session, cmd, "Get org by CML")
		if ret == 0:
			org_in_cml = output.split(":")[1].strip()
			logging.info("It's successful to get org %s by CML" % org_in_cml)
		else:
			raise error.TestFail("Test Failed - Failed to get org by CML.")
		if self.check_element_exist("system-facts-dialog", "lbl", org_in_cml):
			return True
		else:
			return False

	def check_system_uuid_displayed_in_facts(self, session):
		cmd = "subscription-manager identity | grep 'Current identity is'"
		(ret, output) = eu().runcmd(session, cmd, "get system identity")
		if ret == 0:
			system_uuid = output.split(":")[1].strip()
			logging.info("It's successful to get system identity %s by CML" % system_uuid)
		else:
			raise error.TestFail("Test Failed - Failed to get system identity by CML.")
		if self.get_facts_value_by_name("system.uuid") == system_uuid:
			return True
		else:
			return False

	def get_facts_value_by_name(self, facts_name):
		if self.get_os_release() == "6.4":
			for row in range(ldtp.getrowcount(self.get_window("system-facts-dialog"), self.get_table("facts-view-table"))):
				if(ldtp.getcellvalue(self.get_window("system-facts-dialog"), self.get_table("facts-view-table"), row, 0).strip() == facts_name):
					logging.info("get_facts_value_by_name")
					return ldtp.getcellvalue(self.get_window("system-facts-dialog"), self.get_table("facts-view-table"), row, 1)
			raise error.TestFail("Test Failed - Failed to get_facts_value_by_name.")

	def check_server_url(self, server_url):
		if ldtp.gettextvalue(self.get_window("register-dialog"), self.get_text("server-url-text")) == server_url:
			return True
		else:
			return False
			
	 ### firstboot gui
	def welcome_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		if self.check_object_exist('firstboot-main-window', 'firstboot-agr-button'):
			logging.info("It's successful to click welcome-forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check agree-license-button")

	def license_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		if self.check_object_exist('firstboot-main-window', 'firstboot-registeration-warning-label') or self.check_object_exist("firstboot-main-window", "firstboot-register-now-button"):
			logging.info("It's successful to click license-forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check registeration-warning-label or register-now-button")
			
	def software_update_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		if self.check_object_exist('firstboot-main-window', "firstboot_creat_user-label") or self.check_object_exist('firstboot-main-window', "firstboot-register-rhsm-button"):
			logging.info("It's successful to click software_update_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot_creat_user-label or firstboot-register-rhsm-button")

	def create_user_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		self.check_window_exist('firstboot-wng-dialog')
		if self.check_object_exist('firstboot-wng-dialog', 'firstboot-wng-dialog'):
			logging.info("It's successful to click create_user_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check create-user-warning-dialog")
			
	def donot_set_user_yes_button(self):
		self.click_button('firstboot-wng-dialog', 'firstboot-yes-button')
		if not self.check_object_exist('firstboot-wng-dialog', 'firstboot-wng-dialog'):
			logging.info("It's successful to click donot_set_user_yes_button")
		else:
			raise error.TestFail("TestFailed - Failed to check create-user-warning-dialog disappear")

	def date_time_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		self.check_window_exist('firstboot-err-dialog')
		if self.check_object_exist('firstboot-err-dialog', 'firstboot-err-dialog'):
			logging.info("It's successful to click date_time_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check date-time-error-dialog")

	def kdump_ok_button(self):
		self.click_button('firstboot-err-dialog', 'firstboot-ok-button')
		if not self.check_object_exist('firstboot-err-dialog', 'firstboot-err-dialog'):
			logging.info("It's successful to click kdump_ok_button")
		else:
			raise error.TestFail("TestFailed - Failed to check date-time-error-dialog disappear")

	def kdump_finish_button(self):
		self.click_button('firstboot-main-window', 'firstboot-finish-button')
		if not self.check_object_exist("firstboot-main-window", "firstboot-main-window"):
			logging.info("It's successful to click kdump_finish_button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot-main-window disappear")
	
	def choose_service_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		time.sleep(10)
		if self.check_object_exist('firstboot-main-window', "firstboot_activationkey-checkbox") or self.check_object_exist('firstboot-main-window', "classic-login-text"):
			logging.info("It's successful to click choose_service_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot_activationkey-checkbox")

	def registeration_with_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		if self.check_object_exist('firstboot-main-window', "firstboot-manual-checkbox"):
			logging.info("It's successful to click registeration_with_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot-manual-checkbox")

	def input_firstboot_username(self, username):
		self.input_text("firstboot-main-window", "firstboot-login-text", username)
		logging.info("It's successful to input username")

	def input_firstboot_password(self, password):
		self.input_text("firstboot-main-window", "firstboot-password-text", password)
		logging.info("It's successful to input password")

	def check_firstboot_manual(self):
		self.check_checkbox("firstboot-main-window", "firstboot-manual-checkbox")
		logging.info("It's successful to check manual-attach-checkbox")

	def enter_account_info_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		time.sleep(20)
		if self.check_object_exist('firstboot-main-window', 'firstboot-skip-auto-label'):
			logging.info("It's successful to click enter_account_info_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot-skip-auto-label")

	def skip_auto_forward_click(self):
		self.click_button('firstboot-main-window', 'firstboot-fwd-button')
		time.sleep(10)
		if self.check_object_exist("firstboot-main-window", "firstboot_creat_user-label"):
			logging.info("It's successful to click skip_auto_forward button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot_creat_user-label")
			
	def select_classic_mode(self):
		self.click_button('firstboot-main-window', 'firstboot-classic-select-button')
		logging.info("It's successful to click classic mode registeration button")
		
	def input_firstboot_classic_username(self, username):
		self.input_text("firstboot-main-window", "classic-login-text", username)
		logging.info("It's successful to input classic username")
			
	def input_firstboot_classic_password(self, password):
		self.input_text("firstboot-main-window", "classic-password-text", password)
		logging.info("It's successful to input classic password")
	
	def firstboot_classic_redhat_account_forward_button_click(self):
		self.click_button('firstboot-main-window', 'classic-forward-button')
		time.sleep(20)
		if self.check_object_exist("firstboot-main-window", "classic-OS-realeaseversion-label"):
			logging.info("It's successful to click redhat-account-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable redhat-account-forward-label")
			
	def firstboot_classic_os_release_forward_button_click(self):
		self.click_button('firstboot-main-window', 'classic-forward-button')
		if self.check_object_exist('firstboot-main-window', "classic-set-systemname-text"):
			logging.info("It's successful to click firstboot-classic-os-release-forward-button")
		else:
			raise error.TestFail("TestFailed - Failed to check system text")
			
	def firstboot_classic_profile_forward_button_click(self):
		self.click_button('firstboot-main-window', 'classic-forward-button')
		time.sleep(70)
		if self.check_object_exist('firstboot-main-window', "firstboot-classic-reviewsubscription-label"):
			logging.info("It's successful to click firstboot_classic_profile_forward_button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot-classic-reviewsubscription-label")
			
	def firstboot_classic_input_systemname(self):
		self.input_text("firstboot-main-window", "classic-set-systemname-text", "zhangqq")
		logging.info("It's successful to set system name")
	
	def firstboot_classic_reviewsubscription_forward_button_click(self):
		self.click_button('firstboot-main-window', 'classic-forward-button')
		if self.check_object_exist('firstboot-main-window', "firstboot-classic-finishupdate-label"):
			logging.info("It's successful to click firstboot_classic_profile_forward_button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot-classic-finishupdate-label")
			
	def firstboot_classic_finishupdate_forward_button_click(self):
		self.click_button('firstboot-main-window', 'classic-forward-button')
		if self.check_object_exist('firstboot-main-window', "firstboot_creat_user-label"):
			logging.info("It's successful to click finishupdate_forward_button")
		else:
			raise error.TestFail("TestFailed - Failed to check firstboot_creat_user-label")
			
	### rhn_classic register and unregister function
	
	def register_rhn_classic(self, session,username, password):
		
		#open rhn_register gui
		self.set_os_release(session)
		ldtp.launchapp("rhn_register")
		self.check_window_exist("classic-main-window")
		if self.check_object_status("classic-main-window", "classic-software-update-label", 'ENABLED'):
			logging.info("It's successful to open rhn-classic-registeration-gui")
		else:
			raise error.TestFail("TestFailed - TestFailed to open rhn-classic-registeration-gui")

		#click software-update-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		if self.check_object_status("classic-main-window", "classic-choose-service-label", 'ENABLED'):
			logging.info("It's successful to click softwaref update forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable classic-software-update-label")
		
		#click choose-service-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		time.sleep(5)
		if self.check_object_status("classic-main-window", "classic-redhat-account-label", 'ENABLED'):
			logging.info("It's successful to click choose-service-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable classic-redhat-account-label")

		#input account info
		self.input_text("classic-main-window", "classic-login-text", username)
		logging.info("It's successful to input username")
		self.input_text("classic-main-window", "classic-password-text", password)
		logging.info("It's successful to input password")

		#click redhat-account-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		time.sleep(20)
		if self.check_object_status("classic-main-window", "classic-OS-realeaseversion-label", 'ENABLED'):
			logging.info("It's successful to click redhat-account-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable redhat-account-forward-label")
			
		#click OS-releaseversion-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		self.check_window_exist("classic-confirm-osrelease-window")
		if self.check_object_exist("classic-confirm-osrelease-window", "classic-confirm-osrelease-window"):
			logging.info("It's successful to click OS-releaseversion-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to prompt classic-confirm-osrelease-window")

		#click classic-confirm-osrelease-window yes-continue button
		self.click_button('classic-confirm-osrelease-window', 'classic-confirm-osrelease-yes-button')
		time.sleep(10)
		if self.check_object_status("classic-main-window", "classic-create-profile-label", 'ENABLED'):
			logging.info("It's successful to click classic-confirm-osrelease-window yes-continue button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable classic-confirm-osrelease-window yes-continue button")
		
		#set system name
		self.input_text("classic-main-window", "classic-set-systemname-text", "zhangqq")
		logging.info("It's successful to set system name")

		#click create-profile-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		time.sleep(50)
		if self.check_object_status("classic-main-window", "classic-review-subscription-label", 'ENABLED'):
			logging.info("It's successful to click create-profile-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to enable classic-review-subscription-label")

		#click review-subscription-forward button
		self.click_button('classic-main-window', 'classic-forward-button')
		if self.check_object_exist("classic-updates-configured-window", "classic-updates-configured-window"):
			logging.info("It's successful to click review-subscription-forward button")
		else:
			raise error.TestFail("TestFailed - TestFailed to prompt updates-configured-window")

		#click updates-configured-finish button
		self.click_button('classic-updates-configured-window', 'classic-updates-configured-finish-button')
		if not self.check_object_exist("classic-updates-configured-window", "classic-updates-configured-window"):
			logging.info("It's successful to register using firstboot with rhn-classic mode")
		else:
			raise error.TestFail("TestFailed - TestFailed to close updates-configured window")
			
	def unregister_rhn_classic(self, session):
		cmd= "subscription-manager identity"
		(ret, output) = eu().runcmd(session, cmd, "subscription-manager identity")
		if ret == 0 and "server type: RHN Classic" in output:
			logging.info("It's successful to check the system has been registered with rhn_classic mode, and begin to unregister now")
		else:
			raise error.TestFail("TestFailed - TestFailed to check if the system has been registered with rhn_classic mode")


		cmd = "rm -f /etc/sysconfig/rhn/systemid"
		(ret, output) = eu().runcmd(session, cmd, "run rm -f /etc/sysconfig/rhn/systemid")
		if ret == 0:
			logging.info("It's successful to remove /etc/sysconfig/rhn/systemid")


		cmd = "sed -i 's/enabled =.*/enabled = 0/g' /etc/yum/pluginconf.d/rhnplugin.conf"
		(ret, output) = eu().runcmd(session, cmd, "configure rhnplugin.conf")
		if ret == 0:
			logging.info("It's successful to configure /etc/yum/pluginconf.d/rhnplugin.conf")


		cmd= "subscription-manager identity"
		(ret, output) = eu().runcmd(session, cmd, "subscription-manager identity")
		if "server type: RHN Classic" not in output:
			logging.info("It's successful to unregister rhn_classic")
		else:
			raise error.TestFail("TestFailed - TestFailed to unregister rhn_classic")


	# ========================================================
	# 	2. LDTP GUI test common functions
	# ========================================================
	redhat_release_version = "6"
	def set_os_release(self, session):
		global redhat_release_version
		# figure out redhat release
		cmd = "cat /etc/redhat-release"
		(ret, output) = eu().runcmd(session, cmd, "figure out redhat release")
		if ret == 0 and "release 6.4" in output:
			logging.info("Redhat release version is : release 6.4")	
			redhat_release_version = "6.4"
		elif ret == 0 and "release 6.3" in output:
			logging.info("Redhat release version is : release 6.3")
			redhat_release_version = "6.3"
		elif ret == 0 and "release 5.10" in output:
			logging.info("Redhat release version is : release 5.10")
			redhat_release_version = "5.10"
		else:
			raise error.TestFail("Test Failed - Failed to get Redhat release version.")

	def get_os_release(self):
		global redhat_release_version
		# print "redhat_release_version is %s" % redhat_release_version
		# figure out redhat release
		return redhat_release_version

	def restore_gui_environment(self, session):
		# close subscription-manager-gui
		cmd = "killall -9 subscription-manager-gui"
		(ret, output) = eu().runcmd(session, cmd, "close subscription-manager-gui")
		if ret == 0:
			logging.info("It's successful to close subscription-manager-gui.")
		# unregister system
		eu().sub_unregister(session)

	def capture_image(self, image_name="", window=""):
		# capture image to virtlab and name it by time
		time.sleep(5.0)
		image_path = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/results/"
		picture_name = time.strftime('%Y%m%d%H%M%S') + "-" + image_name + ".png"
		ldtp.imagecapture(window, image_path + picture_name)
		logging.info("capture image: %s to log directory" % picture_name)

	def list_objects(self, window):
		logging.info("get objects list in window: %s" % window)
		all_objects_list = self.parse_objects(ldtp.getobjectlist(self.get_window(window)))
		self.show_object_list(all_objects_list)
		# return all_objects_list

	def parse_objects(self, objects_list):
		logging.info("parse objects list")
		window_list = []
		tab_list = []
		button_list = []
		table_list = []
		text_list = []
		menu_list = []
		checkbox_list = []
		label_list = []
		others_list = []
		parsed_objects_list = [window_list, tab_list, button_list, table_list, text_list, menu_list, checkbox_list, label_list, others_list]
		for item in objects_list:
			if item.startswith("frm") or item.startswith("dlg"):
				window_list.append(item)
			elif item.startswith("ptab"):
				tab_list.append(item)
			elif item.startswith("btn"):
				button_list.append(item)
			elif item.startswith("ttbl") or item.startswith("tbl"):
				table_list.append(item)
			elif item.startswith("txt"):
				text_list.append(item)
			elif item.startswith("mnu"):
				menu_list.append(item)
			elif item.startswith("chk"):
				checkbox_list.append(item)
			elif item.startswith("lbl"):
				label_list.append(item)
			else:
				others_list.append(item)
		return parsed_objects_list

	def show_object_list(self, all_objects_list):
		print all_objects_list

	def check_consumer_cert_files(self, session, exist=True):
		cmd = "ls /etc/pki/consumer"
		(ret, output) = eu().runcmd(session, cmd, "check certificate files in /etc/pki/consumer")
		if exist:
			if ret == 0 and output.strip() == "cert.pem  key.pem":
				return True
				logging.info("It is successful to check certificate files in /etc/pki/consumer!")
			else:
				raise error.TestFail("Failed to check certificate files in /etc/pki/consumer!")
		else:
			if not ret == 0 :
				return True
				logging.info("It is successful to check certificate files in /etc/pki/consumer!")
			else:
				raise error.TestFail("Failed to check certificate files in /etc/pki/consumer!")

	def check_table_value_exist(self, window, table, cellvalue):
		return ldtp.doesrowexist(self.get_window(window), self.get_table(table), cellvalue)
		
	def get_window(self, name):
		if name + "-" + self.get_os_release() in ee().get_window.keys():
			return ee().get_window[name + "-" + self.get_os_release()]
		else:
			return ee().get_window[name + "-" + self.get_os_release().split('.')[0]]

	def get_tab(self, name):
		if name + "-" + self.get_os_release() in ee().get_tab.keys():
			return ee().get_tab[name + "-" + self.get_os_release()]
		else:
			return ee().get_tab[name + "-" + self.get_os_release().split('.')[0]]

	def get_button(self, name):
		if name + "-" + self.get_os_release() in ee().get_button.keys():
			return ee().get_button[name + "-" + self.get_os_release()]
		else:
			return ee().get_button[name + "-" + self.get_os_release().split('.')[0]]

	def get_table(self, name):
		if name + "-" + self.get_os_release() in ee().get_table.keys():
			return ee().get_table[name + "-" + self.get_os_release()]
		else:
			return ee().get_table[name + "-" + self.get_os_release().split('.')[0]]

	def get_text(self, name):
		if name + "-" + self.get_os_release() in ee().get_text.keys():
			return ee().get_text[name + "-" + self.get_os_release()]
		else:
			return ee().get_text[name + "-" + self.get_os_release().split('.')[0]]

	def get_menu(self, name):
		if name + "-" + self.get_os_release() in ee().get_menu.keys():
			return ee().get_menu[name + "-" + self.get_os_release()]
		else:
			return ee().get_menu[name + "-" + self.get_os_release().split('.')[0]]

	def get_checkbox(self, name):
		if name + "-" + self.get_os_release() in ee().get_checkbox.keys():
			return ee().get_checkbox[name + "-" + self.get_os_release()]
		else:
			return ee().get_checkbox[name + "-" + self.get_os_release().split('.')[0]]

	def get_label(self, name):
		if name + "-" + self.get_os_release() in ee().get_label.keys():
			return ee().get_label[name + "-" + self.get_os_release()]
		else:
			return ee().get_label[name + "-" + self.get_os_release().split('.')[0]]

	def get_combobox(self, name):
		if name + "-" + self.get_os_release() in ee().get_combobox.keys():
			return ee().get_combobox[name + "-" + self.get_os_release()]
		else:
			return ee().get_combobox[name + "-" + self.get_os_release().split('.')[0]]

	def get_element(self, name):
		if name + "-" + self.get_os_release() in ee().get_element.keys():
			return ee().get_element[name + "-" + self.get_os_release()]
		else:
			return ee().get_element[name + "-" + self.get_os_release().split('.')[0]]

	def get_progressbar(self, name):
                if name + "-" + self.get_os_release() in ee().get_progressbar.keys():
                        return ee().get_progressbar[name + "-" + self.get_os_release()]
                else:
                        return ee().get_progressbar[name + "-" + self.get_os_release().split('.')[0]]

	def click_button(self, window, button_name):
		ldtp.click(self.get_window(window), self.get_button(button_name))

	def click_menu(self, window, menu_name):
		ldtp.click(self.get_window(window), self.get_menu(menu_name))

	def check_checkbox(self, window, checkbox_name):
		ldtp.check(self.get_window(window), self.get_checkbox(checkbox_name))

	def uncheck_checkbox(self, window, checkbox_name):
		ldtp.uncheck(self.get_window(window), self.get_checkbox(checkbox_name))

	def verifycheck_checkbox(self, window, checkbox_name):
		return ldtp.verifycheck(self.get_window(window), self.get_checkbox(checkbox_name))

	def close_window(self, window):
		ldtp.closewindow(self.get_window(window))
		self.check_window_closed(window)

	def check_window_closed(self, window):
		ldtp.waittillguinotexist(self.get_window(window))

	def check_window_exist(self, window):
		ldtp.waittillguiexist(self.get_window(window))
		
	def check_window_open(self, window):
		self.check_window_exist(window)
		logging.info("check_window_open")
		return ldtp.guiexist(self.get_window(window))

	def check_element_exist(self, window, type, name):
		logging.info("check_element_exist")
		return ldtp.guiexist(self.get_window(window), type + name)

	def check_object_exist(self, window, object_name):
		logging.info("check_object_exist")
		object_type = object_name.split("-")[-1]
		if object_type == "window" or object_type == "dialog":
			return ldtp.guiexist(self.get_window(window))
		# elif object_name[:4] == "ptab":
		# 	return ldtp.guiexist(self.get_window(window), self.get_tab(object_name))
		elif object_type == "button":
			return ldtp.guiexist(self.get_window(window), self.get_button(object_name))
		elif object_type == "table":
			return ldtp.guiexist(self.get_window(window), self.get_table(object_name))
		elif object_type == "text":
			return ldtp.guiexist(self.get_window(window), self.get_text(object_name))
		elif object_type == "menu":
			return ldtp.guiexist(self.get_window(window), self.get_menu(object_name))
		elif object_type == "checkbox":
			return ldtp.guiexist(self.get_window(window), self.get_checkbox(object_name))
		elif object_type == "label":
			return ldtp.guiexist(self.get_window(window), self.get_label(object_name))
		elif object_type == "combobox":
			return ldtp.guiexist(self.get_window(window), self.get_combobox(object_name))
		elif object_type == "progressbar":
                        return ldtp.guiexist(self.get_window(window),self.get_progressbar(object_name))

	def check_object_status(self, window, object_name, status):
		if status == "ENABLED":
			real_status = ldtp.state.ENABLED
		elif status == "VISIBLE":
			real_status = ldtp.state.VISIBLE
		object_type = object_name.split("-")[-1]
		if object_type == "window" or object_type == "dialog":
			return ldtp.hasstate(self.get_window(window), real_status)
		# elif object_name[:4] == "ptab":
		# 	return ldtp.hasstate(self.get_window(window), self.get_tab(object_name), real_status)
		elif object_type == "button":
			return ldtp.hasstate(self.get_window(window), self.get_button(object_name), real_status)
		elif object_type == "table":
			return ldtp.hasstate(self.get_window(window), self.get_table(object_name), real_status)
		elif object_type == "text":
			return ldtp.hasstate(self.get_window(window), self.get_text(object_name), real_status)
		elif object_type == "menu":
			return ldtp.hasstate(self.get_window(window), self.get_menu(object_name), real_status)
		elif object_type == "checkbox":
			return ldtp.hasstate(self.get_window(window), self.get_checkbox(object_name), real_status)
		elif object_type == "label":
			return ldtp.hasstate(self.get_window(window), self.get_label(object_name), real_status)

	def wait_until_button_enabled(self, window, button_name):
		if self.get_os_release().split('.')[0] == "5" or self.get_os_release() == "6.4":
			while ldtp.hasstate(self.get_window(window), self.get_button(button_name), ldtp.state.ENABLED) == 0:
				ldtp.wait(5)

	def input_text(self, window, text, text_value):
		ldtp.settextvalue(self.get_window(window), self.get_text(text), text_value)

	def verify_text(self, window, text, text_value):
		ldtp.verifysettext(self.get_window(window), self.get_text(text), text_value)

	def click_tab(self, tab_name):
		ldtp.selecttab(self.get_window("main-window"), self.get_tab("all-tabs"), self.get_tab(tab_name))

	def get_table_row_count(self, window, table_name):
		return ldtp.getrowcount(self.get_window(window), self.get_table(table_name))

	def get_table_cell(self, window, table_name, row, colomn):
		return ldtp.getcellvalue(self.get_window(window), self.get_table(table_name), row, colomn)

	def sendkeys(self, key1, key2="", key3=""):
		ldtp.keypress(key1)
		if not key2 == "":
			ldtp.keypress(key2)
			if not key3 == "":
				ldtp.keypress(key3)
				ldtp.keyrelease(key3)
			ldtp.keyrelease(key2)
		ldtp.keyrelease(key1)

	def wait_seconds(self, seconds):
		ldtp.wait(seconds)
