
from ..base_component import BaseComponent

class TextBox(BaseComponent):
    """
    Entity-Component: TextBox
    """

    def __init__(self, browser, container, encrypted=False):
        """
            :param browser: The selenium webdriver
            :param container: The locator of the container where the control is located in. 
        """
        super(TextBox, self).__init__(browser, container)
        self.encrypted = encrypted

    def set_value(self, value):
        """
        set value of the textbox
        """

        self.container.clear()
        self.container.send_keys(value)

    def get_value(self):
        """
        get value from the textbox
        """
        return self.container.get_attribute('value').strip()

    def is_editable(self):
        '''
        Returns True if the Textbox is editable, False otherwise
        '''
        return not bool(self.container.get_attribute("readonly") or self.container.get_attribute("disabled"))


    def clear_text(self):
        '''
        Clears the textbox value
        '''
        self.container.clear()