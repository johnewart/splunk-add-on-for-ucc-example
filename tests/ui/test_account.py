from pytest_splunk_addon_ui_smartx.base_test import UccTester
from pytest_splunk_addon_ui_smartx.backend_confs import BackendConf
from .Example_UccLib.account import AccountPage
from .Example_UccLib.input_page import InputPage

import random
import pytest
import re
import time
import configparser
import os
import requests
import urllib
import copy


ACCOUNT_CONFIG = {
    'name': 'TestAccount',
    'account_checkbox': 1,
    'account_multiple_select': 'one',
    'account_radio': 'yes',
    'auth_type': 'basic',
    'custom_endpoint': 'login.example.com',
    'username': 'TestUser',
    'password': 'TestPassword',
    'token': 'TestToken',
    'disabled': 0,
    'client_id': '',
    'client_secret': '',
    'redirect_url': '',
    'endpoint': '',
    'oauth_state_enabled': '',
    'example_help_link': ''
}

@pytest.fixture
def add_input(ucc_smartx_configs):
    input_page = InputPage(ucc_smartx_configs, open_page=False)
    url = input_page._get_input_endpoint()
    kwargs = {
        'name': 'example_input_one://dummy_input_one',
        'account':'TestAccount',
        'input_one_checkbox': '1',
        'input_one_radio': '1',
        'interval': '90',
        'limit': '1000',
        'multipleSelectTest': 'a|b',
        'object': 'test_object',
        'object_fields': 'test_field',
        'order_by': 'LastModifiedDate',
        'singleSelectTest': 'two',
        'start_date': '2020-12-11T20:00:32.000z',
        'disabled': 0,
    }
    yield input_page.backend_conf.post_stanza(url, kwargs)

@pytest.fixture
def add_account(ucc_smartx_configs):
    account = AccountPage(ucc_smartx_configs, open_page=False)
    url = account._get_account_endpoint()
    kwargs = ACCOUNT_CONFIG
    yield account.backend_conf.post_stanza(url, kwargs)

@pytest.fixture
def add_multiple_account(ucc_smartx_configs):
    account = AccountPage(ucc_smartx_configs, open_page=False)
    url = account._get_account_endpoint()
    for i in range(12):
        kwargs = copy.deepcopy(ACCOUNT_CONFIG)
        kwargs['name'] = kwargs['name'] + str(i)
        account.backend_conf.post_stanza(url, kwargs)

@pytest.fixture(autouse=True)
def delete_accounts(ucc_smartx_configs):
    yield
    account = AccountPage(ucc_smartx_configs)
    account.backend_conf.delete_all_stanzas()
    

class TestAccount(UccTester):
    
    @pytest.mark.account
    # Verifies sorting functionality for name column
    def test_account_sort_functionality(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.sort_column("Name")
        sort_order = account.table.get_sort_order()
        column_values = list(account.table.get_column_values("Name"))
        column_values = list(str(item)for item in column_values)
        sorted_values = sorted(column_values , key = str.lower)
        self.assert_util(
            sort_order["header"].lower(),
            'name',
            msg="Found : {} Expected : {}".format(
                sort_order["header"].lower(),
                'name'
                )
            )
        self.assert_util(
            column_values,
            sorted_values,
            msg="Found : {} Expected : {}".format(column_values, sorted_values)
            )
        assert sort_order["ascending"]
        
    @pytest.mark.account
    # Verifies count on table
    def test_account_count(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        self.assert_util(
            account.table.get_count_title,
            "{} Items".format(len(account.backend_conf.get_all_stanzas())),
            msg="Found : {} Expected : {}".format(
                account.table.get_count_title(),
                "{} Items".format(len(account.backend_conf.get_all_stanzas()))
                )
            )

    @pytest.mark.account
    # Verifies the frontend after adding account
    def test_account_add_frontend_validation(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG['name'])
        account.entity.username.set_value(ACCOUNT_CONFIG['username'])
        account.entity.multiple_select.select("Option One")
        account.entity.password.set_value(ACCOUNT_CONFIG['password'])
        account.entity.security_token.set_value("TestToken")
        assert account.entity.save()
        self.assert_util(
            account.table.get_table()[ACCOUNT_CONFIG['name']],
            {
                'name': ACCOUNT_CONFIG['name'],
                'auth type': 'basic',
                'actions': 'Edit | Clone | Delete'
            },
            msg="Found : {} Expected : {}".format(
                account.table.get_table()[ACCOUNT_CONFIG['name']],
                {
                'name': ACCOUNT_CONFIG['name'],
                'auth type': 'basic',
                'actions': 'Edit | Clone | Delete'
                }
                )
            )

    @pytest.mark.account
    # Verifies the filter functionality (Negative)
    def test_accounts_filter_functionality_negative(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.set_filter("heloo")
        self.assert_util(
            account.table.get_count_title,
            "{} Items".format(account.table.get_row_count()),
            msg="Found : {} Expected : {}".format(
                account.table.get_count_title(),
                "{} Items".format(account.table.get_row_count())
                )
            )
        account.table.clean_filter()
        
    @pytest.mark.account
    # Verifies the filter functionality (Positive)
    def test_accounts_filter_functionality_positive(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.set_filter("TestAccount")
        self.assert_util(
            account.table.get_count_title,
            "{} Items".format(account.table.get_row_count()),
            msg="Found : {} Expected : {}".format(
                account.table.get_count_title(),
                "{} Items".format(account.table.get_row_count())
                )
            )
        account.table.clean_filter()

    @pytest.mark.account
    # Verifies the default number of rows in the table
    def test_account_default_rows_in_table(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        self.assert_util(
            account.table.get_row_count,
            0,
            msg="Found : {} Expected : {}".format(
                account.table.get_row_count(),
                0
                )
            )

    @pytest.mark.account
    # Verifies the title and description of the page
    def test_account_title_and_description(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        self.assert_util(
            account.title.wait_to_display,
            "Configuration",
            msg="Found : {} Expected : {}".format(
                account.title.wait_to_display(),
                "Configuration"
                )
            )
        self.assert_util(
            account.description.wait_to_display,
            "Set up your add-on",
            msg="Found : {} Expected : {}".format(
                account.description.wait_to_display(),
                "Set up your add-on"
                )
            )

    @pytest.mark.account
    # Verifies the title of the 'Add Entity'
    def test_account_add_valid_title(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
            account.entity.title.container.get_attribute('textContent').strip(),
            "Add Account",
            msg="Found : {} Expected : {}".format(
                account.entity.title.container.get_attribute('textContent').strip(),
                "Add Account"
                )
            )

    @pytest.mark.account
    # Verifies the title of the 'Edit Entity'
    def test_account_edit_valid_title(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
            account.entity.title.container.get_attribute('textContent').strip(),
            "Update Account",
            msg="Found : {} Expected : {}".format(
                account.entity.title.container.get_attribute('textContent').strip(),
                "Update Account"
                )
            )

    @pytest.mark.account
    # Verifies the title of the 'Clone Entity'
    def test_account_clone_valid_title(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
            account.entity.title.container.get_attribute('textContent').strip(),
            "Clone Account",
            msg="Found : {} Expected : {}".format(
                account.entity.title.container.get_attribute('textContent').strip(),
                "Clone Account"
                )
            )

    @pytest.mark.account
    # Verifies the title of the 'Delete Entity'
    def test_account_delete_valid_title(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"], prompt_msg=True)
        self.assert_util(
            account.entity.title.container.get_attribute('textContent').strip(),
            "Delete Confirmation",
            msg="Found : {} Expected : {}".format(
                account.entity.title.container.get_attribute('textContent').strip(),
                "Delete Confirmation"
                )
            )

    @pytest.mark.account
    # Verifies the prompt message of the 'Delete Entity'
    def test_account_delete_valid_prompt_message(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        prompt_message = account.table.delete_row(ACCOUNT_CONFIG["name"], prompt_msg=True)
        self.assert_util(
            prompt_message,
            'Are you sure you want to delete "{}" ? Ensure that no input is configured with "{}" as this will stop data collection for that input.'.format(ACCOUNT_CONFIG["name"],ACCOUNT_CONFIG["name"]),
            msg="Found : {} Expected : {}".format(
                prompt_message,
                'Are you sure you want to delete "{}" ? Ensure that no input is configured with "{}" as this will stop data collection for that input.'.format(ACCOUNT_CONFIG["name"],ACCOUNT_CONFIG["name"])
                )
            )

    @pytest.mark.account
    # Verifies required field username
    def test_account_required_field_username(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        self.assert_util(
            account.entity.save,
            'Field Username is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Username is required'
                )
            )

    @pytest.mark.account
    # Verifies required field password
    def test_account_required_field_password(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        self.assert_util(
            account.entity.save,
            'Field Password is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Password is required'
                )
            )

    @pytest.mark.account
    # Verifies if the password field is masked or not in the Textbox
    def test_account_encrypted_field_password(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        textbox_type = account.entity.password.get_type()
        self.assert_util(
            textbox_type,
            'password',
            msg="Found : {} Expected : {}".format(
                textbox_type,
                'password'
                )
            )

    @pytest.mark.account
    # Verifies required field name
    def test_account_required_field_name(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        self.assert_util(
            account.entity.save,
            'Field Name is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Name is required'
                )
            )

    @pytest.mark.account
    # Verifies help text for the field name
    def test_account_help_text_name(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        help_text = account.entity.name.get_help_text()
        self.assert_util(
            help_text,
            'Enter a unique name for this account.',
            msg="Found : {} Expected : {}".format(
                help_text,
                'Enter a unique name for this account.'
                )
            )

    @pytest.mark.account
    # Verifies required field example environment
    def test_account_required_field_example_environment(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.environment.cancel_selected_value()
        self.assert_util(
            account.entity.save,
            'Field Example Environment is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Example Environment is required'
                )
            )

    @pytest.mark.account
    # Verifies required field example multiple select
    def test_account_required_field_example_multiple_select(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value("TestMultiAccount")
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        self.assert_util(
            account.entity.save,
            'Field Example Multiple Select is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Example Multiple Select is required'
                )
            )
    
    @pytest.mark.account
    # Verifies required field client id
    def test_account_required_field_client_id(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.auth_key.select('OAuth 2.0 Authentication')
        self.assert_util(
            account.entity.save,
            'Field Client Id is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Client Id is required'
                )
            )
    
    @pytest.mark.account
    # Verifies required field client secret
    def test_account_required_field_client_secret(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.auth_key.select('OAuth 2.0 Authentication')
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option One")
        account.entity.client_id.set_value("TestClientId")
        self.assert_util(
            account.entity.save,
            'Field Client Secret is required',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Field Client Secret is required'
                )
            )

    @pytest.mark.account
    # Verifies if the password field is masked or not in the Textbox
    def test_account_encrypted_field_client_secret(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.auth_key.select('OAuth 2.0 Authentication')
        textbox_type = account.entity.client_secret.get_type()
        self.assert_util(
            textbox_type,
            'password',
            msg="Found : {} Expected : {}".format(
                textbox_type,
                'password'
                )
            )

    @pytest.mark.account
    # Verifies whether adding special characters, number in starting of name field displays validation error
    def test_account_valid_account_name(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.name.set_value("123TestAccount")
        self.assert_util(
            account.entity.save,
            'Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.'
                )
            )

    @pytest.mark.account
    # Verifies the name field should not be more than 50 characters
    def test_account_valid_length_name(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.name.set_value("TestUserTestUserTestUserTestUserTestUserTestUserTestUserTestUser")
        self.assert_util(
            account.entity.save,
            'Length of ID should be between 1 and 50',
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                account.entity.save(expect_error=True),
                'Length of ID should be between 1 and 50'
                )
            )

    @pytest.mark.account
    # Verifies default value of example environment
    def test_account_default_value_example_environment(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        self.assert_util(
            account.entity.environment.get_value,
            "Value1",
            msg="Found : {} Expected : {}".format(
                account.entity.environment.get_value(),
                "Value1"
                )
            )

    @pytest.mark.account
    # Verifies example environment list dropdown
    def test_account_list_example_environment(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
            set(account.entity.environment.list_of_values()),
            {"Value1", "Value2", "Other"},
            msg="Found : {} Expected : {}".format(
                set(account.entity.environment.list_of_values()),
                {"Value1", "Value2", "Other"}
                )
            )

    @pytest.mark.account
    # Verifies default value of auth type
    def test_account_default_value_auth_type(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
            account.entity.auth_key.get_value,
            "basic",
            msg="Found : {} Expected : {}".format(
                account.entity.auth_key.get_value(),
                "basic"
                )
            )

    @pytest.mark.account
    # Verifies auth type list dropdown
    def test_account_list_auth_type(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
                    set(account.entity.auth_key.list_of_values()),
                    {"Basic Authentication", "OAuth 2.0 Authentication"},
                    msg="Found : {} Expected : {}".format(
                        set(account.entity.auth_key.list_of_values()),
                        {"Basic Authentication", "OAuth 2.0 Authentication"}
                        )
                    )

    @pytest.mark.account
    # Verifies Check/Uncheck in example checkbox
    def test_account_checked_example_checkbox(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.example_checkbox.check()
        self.assert_util(
                    account.entity.example_checkbox.is_checked,
                    True,
                    msg="Found : {} Expected : {}".format(
                        account.entity.example_checkbox.is_checked(),
                        True
                        )
                    )
        account.entity.example_checkbox.uncheck()
        self.assert_util(
                    account.entity.example_checkbox.is_checked,
                    False,
                    msg="Found : {} Expected : {}".format(
                        account.entity.example_checkbox.is_checked(),
                        False
                        )
                    )
        
    @pytest.mark.account
    # Verifies example environment select value
    def test_account_select_value_example_environment(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.environment.select("Value2")
        self.assert_util(
                    account.entity.environment.get_value,
                    "Value2",
                    msg="Found : {} Expected : {}".format(
                        account.entity.environment.get_value(),
                        "Value2"
                        )
                    )

    @pytest.mark.account
    # Verifies example multiple select list dropdown
    def test_account_list_example_multiple_select(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
                    set(account.entity.multiple_select.list_of_values()),
                    {"Option One", "Option Two"},
                    msg="Found : {} Expected : {}".format(
                        set(account.entity.multiple_select.list_of_values()),
                        {"Option One", "Option Two"}
                        )
                    )

    @pytest.mark.account
    # Verifies exampl multiple select value
    def test_account_select_value_example_multiple_select(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.multiple_select.select("Option One")
        account.entity.multiple_select.select("Option Two")
        self.assert_util(
                    account.entity.multiple_select.get_values,
                    ['Option One', 'Option Two'],
                    msg="Found : {} Expected : {}".format(
                        account.entity.multiple_select.get_values(),
                        ['Option One', 'Option Two']
                        )
                    )

    @pytest.mark.account
    # Verifies exampl multiple select seach funtionality
    def test_account_search_value_example_multiple_select(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
                    account.entity.multiple_select.search_get_list,
                    ["Option One"],
                    left_args={'value': "Option One"},
                    msg="Found : {} Expected : {}".format(
                        account.entity.multiple_select.search_get_list("Option One"),
                        ["Option One"]
                        )
                    )
        
    @pytest.mark.account
    # Verifies default value of example radio
    def test_account_default_value_example_radio(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        self.assert_util(
                    account.entity.account_radio.get_value,
                    "Yes",
                    msg="Found : {} Expected : {}".format(
                        account.entity.account_radio.get_value(),
                        "Yes"
                        )
                    )

    @pytest.mark.account
    # Verifies close functionality at time of add
    def test_account_add_close_entity(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert account.entity.close()

    @pytest.mark.account
    # Verifies cancel functionality at time of add
    def test_account_add_cancel_entity(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert account.entity.cancel()

    @pytest.mark.account
    # Verifies close functionality at time of delete
    def test_account_delete_close_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        assert account.table.delete_row(ACCOUNT_CONFIG["name"], close=True)
        
    @pytest.mark.account
    # Verifies cancel functionality at time of delete
    def test_account_delete_cancel_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        assert account.table.delete_row(ACCOUNT_CONFIG["name"], cancel=True)
    
    @pytest.mark.account
    # Verifies close functionality at time of edit
    def test_account_edit_close_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        assert account.entity.close()
        
    @pytest.mark.account
    # Verifies cancel functionality at time of edit
    def test_account_edit_cancel_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        assert account.entity.cancel()
    
    @pytest.mark.account
    # Verifies close functionality at time of clone
    def test_account_clone_close_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        assert account.entity.close()

    @pytest.mark.account
    # Verifies cancel functionality at time of clone
    def test_account_clone_cancel_entity(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        assert account.entity.cancel()
        
    @pytest.mark.account
    # Verifies by saving an entity with duplicate name at time of add it displays and error
    def test_add_account_duplicate_name(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option One")
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.account_radio.select("Yes")
        self.assert_util(
                    account.entity.save,
                    'Name {} is already in use'.format(ACCOUNT_CONFIG["name"]),
                    left_args={'expect_error': True},
                    msg="Found : {} Expected : {}".format(
                        account.entity.save(expect_error=True),
                        'Name {} is already in use'.format(ACCOUNT_CONFIG["name"])
                        )
                    )
        
    @pytest.mark.account
    # Verifies the frontend delete functionlity
    def test_account_delete_row_frontend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        self.assert_util(ACCOUNT_CONFIG["name"],
                         account.table.get_table(),
                         "not in",
                         msg="{} should not be present in {}".format(
                             ACCOUNT_CONFIG["name"],
                             account.table.get_table())
                         )

    @pytest.mark.account
    # Verifies the frontend uneditable fields at time of edit of the account
    def test_account_edit_uneditable_field_name(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
                    account.entity.name.is_editable,
                    False,
                    msg="Found : {} Expected : {}".format(
                        account.entity.name.is_editable(),
                        False
                        )
                    )

    @pytest.mark.account
    # Verifies the frontend edit functionality
    def test_account_edit_frontend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        account.entity.environment.select("Value2")
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestEditUser")
        account.entity.password.set_value("TestEditPassword")
        account.entity.security_token.set_value("TestEditToken")
        account.entity.account_radio.select("No")
        assert account.entity.save()
        self.assert_util(
                    account.table.get_table()[ACCOUNT_CONFIG["name"]] ,
                    {
                        'name': 'TestAccount', 
                        'auth type': 'basic',
                        'actions': 'Edit | Clone | Delete'
                        },
                    msg="Found : {} Expected : {}".format(
                        account.table.get_table()[ACCOUNT_CONFIG["name"]] ,
                        {
                            'name': 'TestAccount', 
                            'auth type': 'basic',
                            'actions': 'Edit | Clone | Delete'
                            }
                        )
                    )
        
    @pytest.mark.account
    # Verifies by saving an entity with duplicate name at time of clone it displays and error
    def test_clone_account_duplicate_name(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        self.assert_util(
                    account.entity.save,
                    'Name {} is already in use'.format(ACCOUNT_CONFIG["name"]),
                    left_args={'expect_error': True},
                    msg="Found : {} Expected : {}".format(
                        account.entity.save(expect_error=True),
                        'Name {} is already in use'.format(ACCOUNT_CONFIG["name"])
                        )
                    )

    @pytest.mark.account
    # Verifies the frontend clone functionality
    def test_account_clone_frontend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
                    account.entity.name.get_value,
                    "",
                    msg="Found : {} Expected : {}".format(
                        account.entity.name.get_value(),
                        ""
                        )
                    )
        account.entity.name.set_value("TestAccount2")
        account.entity.username.set_value("TestUserClone")
        account.entity.password.set_value("TestPasswordClone")
        account.entity.security_token.set_value("TestTokenClone")
        account.entity.account_radio.select("Yes")
        assert account.entity.save()
        self.assert_util(
                    account.table.get_table()["TestAccount2"],
                    {
                        'name': 'TestAccount2', 
                        'auth type': 'basic',
                        'actions': 'Edit | Clone | Delete'
                    },
                    msg="Found : {} Expected : {}".format(
                        account.table.get_table()["TestAccount2"],
                        {
                            'name': 'TestAccount2', 
                            'auth type': 'basic',
                            'actions': 'Edit | Clone | Delete'
                            }
                        )
                    )
                        

    @pytest.mark.account
    # Verifies the frontend default fields at time of clone
    def test_account_clone_default_values(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
                    account.entity.name.get_value,
                    "",
                    msg="Found : {} Expected : {}".format(
                        account.entity.name.get_value(),
                        ""
                        )
                    )
        self.assert_util(
                    account.entity.username.get_value,
                    "TestUser",
                    msg="Found : {} Expected : {}".format(
                        account.entity.username.get_value(),
                        "TestUser"
                        )
                    )
        self.assert_util(
                    account.entity.multiple_select.get_values,
                    ['Option One'],
                    msg="Found : {} Expected : {}".format(
                        account.entity.multiple_select.get_values(),
                        ['Option One']
                        )
                    )
        self.assert_util(
                    account.entity.auth_key.get_value,
                    "basic",
                    msg="Found : {} Expected : {}".format(
                        account.entity.auth_key.get_value(),
                        "basic"
                        )
                    )
    
    @pytest.mark.account
    # Verifies the account in backend after adding account from frontend
    def test_account_add_backend_validation(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.multiple_select.select("Option One")
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.security_token.set_value(ACCOUNT_CONFIG["token"])
        assert account.entity.save()
        self.assert_util(
                    account.backend_conf.get_stanza,
                    {'account_checkbox': '0',
                        'account_multiple_select' : ACCOUNT_CONFIG['account_multiple_select'],
                        'account_radio' : '1',
                        'auth_type' : ACCOUNT_CONFIG['auth_type'],
                        'username' : ACCOUNT_CONFIG["username"],
                        'custom_endpoint': ACCOUNT_CONFIG['custom_endpoint'],
                        'disabled': False,
                        'password': '******',
                        'token': '******'
                    },
                    left_args={'stanza': ACCOUNT_CONFIG["name"]},
                    msg="Found : {} Expected : {}".format(
                        account.backend_conf.get_stanza(ACCOUNT_CONFIG["name"]),
                        {
                            'account_checkbox': '0',
                            'account_multiple_select' : ACCOUNT_CONFIG['account_multiple_select'],
                            'account_radio' : '1',
                            'auth_type' : ACCOUNT_CONFIG['auth_type'],
                            'username' : ACCOUNT_CONFIG["username"],
                            'custom_endpoint': ACCOUNT_CONFIG['custom_endpoint'],
                            'disabled': False,
                            'password': '******',
                            'token': '******'
                            }
                        )
                    )

    @pytest.mark.account
    # Verifies the account in backend after editing account from frontend
    def test_account_edit_backend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestEditUser")
        account.entity.password.set_value("TestEditPassword")
        account.entity.security_token.set_value("TestEditToken")
        account.entity.account_radio.select("No")
        account.entity.save()
        self.assert_util(
                    account.backend_conf.get_stanza,
                    {'account_checkbox': '1',
                        'account_multiple_select' : 'one,two',
                        'account_radio' : '0',
                        'auth_type' : 'basic',
                        'username' : 'TestEditUser',
                        'custom_endpoint': 'login.example.com',
                        'disabled': False,
                        'password': '******',
                        'token': '******'
                    },
                    left_args={'stanza': ACCOUNT_CONFIG["name"]},
                    msg="Found : {} Expected : {}".format(
                        account.backend_conf.get_stanza(ACCOUNT_CONFIG["name"]),
                        {
                            'account_checkbox': '1',
                            'account_multiple_select' : 'one,two',
                            'account_radio' : '0',
                            'auth_type' : 'basic',
                            'username' : 'TestEditUser',
                            'custom_endpoint': 'login.example.com',
                            'disabled': False,
                            'password': '******',
                            'token': '******'
                            }
                        )
                    )

    @pytest.mark.account
    # Verifies the account in backend after cloning account from frontend
    def test_account_clone_backend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        account.entity.name.set_value("TestAccountClone")
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestCloneUser")
        account.entity.password.set_value("TestClonePassword")
        account.entity.security_token.set_value("TestCloneToken")
        account.entity.account_radio.select("No")
        account.entity.save()
        self.assert_util(
                    account.backend_conf.get_stanza,
                    {
                        'account_checkbox': '1',
                        'account_multiple_select' : 'one,two',
                        'account_radio' : '0',
                        'auth_type' : 'basic',
                        'username' : 'TestCloneUser',
                        'custom_endpoint': 'login.example.com',
                        'disabled': False,
                        'password': '******',
                        'token': '******'
                    },
                    left_args={'stanza': "TestAccountClone"},
                    msg="Found : {} Expected : {}".format(
                        account.backend_conf.get_stanza("TestAccountClone"),
                        {
                            'account_checkbox': '1',
                        'account_multiple_select' : 'one,two',
                        'account_radio' : '0',
                        'auth_type' : 'basic',
                        'username' : 'TestCloneUser',
                        'custom_endpoint': 'login.example.com',
                        'disabled': False,
                        'password': '******',
                        'token': '******'
                    }
                        )
                    )
    
    @pytest.mark.account
    # Verifies the account in backend after deleting the account from frontend
    def test_account_delete_row_backend_validation(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        self.assert_util(ACCOUNT_CONFIG["name"],
                         account.backend_conf.get_all_stanzas().keys(),
                         "not in",
                         msg="{} should not be present in {}".format(
                             ACCOUNT_CONFIG["name"],
                             account.backend_conf.get_all_stanzas().keys())
                         )
    
    @pytest.mark.account
    # Verifies pagination list
    def test_account_pagination(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        name_column_page1 = account.table.get_column_values("name")
        account.table.switch_to_next()
        name_column_page2 = account.table.get_column_values("name")
        self.assert_util(name_column_page1,
                         name_column_page2,
                         "!=",
                         msg="{} should not be equal to {}".format(
                             name_column_page1,
                             name_column_page2)
                         )

    @pytest.mark.account
    # Verifies whether the table help link redirects to the correct URL
    def test_account_helplink(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        go_to_link = "https://docs.splunk.com/Documentation"
        account.entity.open()
        self.assert_util(
                account.entity.help_link.go_to_link,
                go_to_link
                )

    @pytest.mark.account
    # Verifies by deleting the input used account
    def test_account_delete_account_in_use(self, ucc_smartx_configs, add_account, add_input):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        self.assert_util(
                    account.table.delete_row(ACCOUNT_CONFIG["name"], prompt_msg=True),
                    r'TestAccount cannot be deleted because it is in use',
                    left_args={'name': ACCOUNT_CONFIG["name"], "prompt_msg": True},

                    msg="Found : {} Expected : {}".format(
                        account.table.delete_row(ACCOUNT_CONFIG["name"], prompt_msg=True),
                        r'TestAccount cannot be deleted because it is in use'
                    )
        )