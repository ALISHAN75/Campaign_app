
import re
class MMPhoneNumber():

    def __init__(self):
        self.OOREDOO = "Ooredoo"
        self.TELENOR = "Telenor"
        self.MYTEL = "MYTEL"
        self.MEC = "MEC"
        self.MPT     = "MPT"
        self.UNKNOWN = "Unknown"

        self.GSM_TYPE = "GSM"
        self.WCDMA_TYPE = "WCDMA"
        self.CDMA_450_TYPE = "CDMA 450 MHz"
        self.CDMA_800_TYPE = "CDMA 800 MHz"

        # self.ooredoo_re = r"^(09|\+?959)9(7|6)\d{7}$"
        # self.telenor_re = r"^(09|\+?959)7(9|8|7|4)\d{7}$"
        # self.mpt_re = r"^(09|\+?959)(5\d{6}|4\d{7,8}|2\d{6,8}|3\d{7,8}|6\d{6}|8\d{6}|7\d{7}|9(0|1|9)\d{5,6})$"
        
        
        self.ooredoo_re = "^(09|\+?959)9([4-9])\d{7}$"
        self.telenor_re = "^(09|\+?959)7([4-9])\d{7}$"
        self.mytel_re = "^(09|\+?959)6([5-9])\d{7}$"
        self.mpt_re = "^(09|\+?959)(5\d{6}|4\d{7,8}|2\d{6,8}|6\d{6}|8\d{6,8}|7\d{7}|9(0|1|9)\d{5,6}|2[0-4]\d{5}|5[0-6]\d{5}|8[13-7]\d{5}|4[1379]\d{6}|73\d{6}|91\d{6}|25\d{7}|26[0-5]\d{6}|40[0-4]\d{6}|42\d{7}|45\d{7}|89[6789]\d{6}|)$"
        self.mec_re = "^(09|\+?959)(3\d{7,8}|3[0-369]\d{6}|34\d{7})"


    def is_valid_mm_phonenumber(self, phonenumber=None):
        if phonenumber:
            phonenumber = self.sanitize_phonenumber(phonenumber=phonenumber)
            mm_phone_re = r"^(09|\+?950?9|\+?95950?9)\d{7,9}$"

            if self.__check_regex([mm_phone_re], phonenumber):
                return True

        return False


    def sanitize_phonenumber(self, phonenumber=None):
        if phonenumber:
            phonenumber = phonenumber.strip()
            phonenumber = phonenumber.replace(" ", "")
            phonenumber = phonenumber.replace("-", "")

            country_code_re = r"^\+?950?9\d+$"

            if self.__check_regex([country_code_re], phonenumber):
                ## try to remove double country code
                double_country_code_re = r"^\+?95950?9\d{7,9}$"

                if self.__check_regex([double_country_code_re], phonenumber):
                    ## remove double country code
                    phonenumber = phonenumber.replace("9595", "95", 1)

                ## remove 0 before area code
                zero_before_areacode_re = r"^\+?9509\d{7,9}$"

                if self.__check_regex([zero_before_areacode_re], phonenumber):
                    ## remove double country code
                    phonenumber = phonenumber.replace("9509", "959", 1)

        return phonenumber


    def get_telecom_name(self, phonenumber=None):
        telecom_name = self.UNKNOWN

        if phonenumber and self.is_valid_mm_phonenumber(phonenumber=phonenumber):
            ## sanitize the phonenumber first
            phonenumber = self.sanitize_phonenumber(phonenumber=phonenumber)

            if self.__check_regex([self.ooredoo_re], phonenumber):
                telecom_name = self.OOREDOO
            elif self.__check_regex([self.telenor_re], phonenumber):
                telecom_name = self.TELENOR
            elif self.__check_regex([self.mytel_re], phonenumber):
                telecom_name = self.MYTEL
            elif self.__check_regex([self.mec_re], phonenumber):
                telecom_name = self.MEC
            elif self.__check_regex([self.mpt_re], phonenumber):
                telecom_name = self.MPT

        return telecom_name



    def get_phone_network_type(self, phonenumber=None):
        network_type = self.UNKNOWN

        if phonenumber and self.is_valid_mm_phonenumber(phonenumber=phonenumber):
            ## sanitize the phonenumber first
            phonenumber = self.sanitize_phonenumber(phonenumber=phonenumber)

            if self.__check_regex([self.ooredoo_re, self.telenor_re, self.mytel_re], phonenumber):
                network_type = self.GSM_TYPE
            elif self.__check_regex([self.mpt_re], phonenumber):
                wcdma_re = r"^(09|\+?959)(55\d{5}|25[2-4]\d{6}|26\d{7}|4(4|5|6)\d{7})$"
                cdma_450_re = r"^(09|\+?959)(8\d{6}|6\d{6}|49\d{6})$"
                cdma_800_re = r"^(09|\+?959)(3\d{7}|73\d{6}|91\d{6})$"

                if self.__check_regex([wcdma_re], phonenumber):
                    network_type = self.WCDMA_TYPE
                elif self.__check_regex([cdma_450_re], phonenumber):
                    network_type = self.CDMA_450_TYPE
                elif self.__check_regex([cdma_800_re], phonenumber):
                    network_type = self.CDMA_800_TYPE
                else:
                    network_type = self.GSM_TYPE

        return network_type


    def __check_regex(self, regex_array, input_string):
        for regex in regex_array:
            if re.search(regex, input_string):
                return True

        return False




# import re

# def is_myanmar_phone_number(phone_number):
#     # Regex pattern for Myanmar phone number
#     pattern = r'^\+959[0-9]{9}$'
#     return re.match(pattern, phone_number) is not None

# # Test the function
# phone_number = "+959444455551"
# if is_myanmar_phone_number(phone_number):
#     print("Valid Myanmar phone number")
# else:
#     print("Invalid Myanmar phone number")

# mm_phonenumber = MMPhoneNumber()
# full_PhoneNumber = '+9591234567' #Country Code is mendatory +95

# if mm_phonenumber.is_valid_mm_phonenumber(phonenumber=full_PhoneNumber):
#     # Send SMS
#     print("Valid Number")
# else:
#     # Show Error Message
#     print("Error")