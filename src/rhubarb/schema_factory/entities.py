# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class Entities:
    ADDRESS = {
        "type": "object",
        "properties": {
            "ADDRESS": {
                "type": "string",
                "description": "A physical address, such as '100 Main Street, Anytown, USA' or 'Suite #12, Building 123'.",
            }
        },
        "required": ["ADDRESS"],
    }

    AGE = {
        "type": "object",
        "properties": {
            "AGE": {
                "type": "string",
                "description": "An individual's age, including the quantity and unit of time.",
            }
        },
        "required": ["AGE"],
    }

    AWS_ACCESS_KEY = {
        "type": "object",
        "properties": {
            "AWS_ACCESS_KEY": {
                "type": "string",
                "description": "A unique identifier that's associated with a secret access key; used to sign programmatic AWS requests cryptographically.",
            }
        },
        "required": ["AWS_ACCESS_KEY"],
    }

    AWS_SECRET_KEY = {
        "type": "object",
        "properties": {
            "AWS_SECRET_KEY": {
                "type": "string",
                "description": "A unique identifier that's associated with an access key.",
            }
        },
        "required": ["AWS_SECRET_KEY"],
    }

    CREDIT_DEBIT_CVV = {
        "type": "object",
        "properties": {
            "CREDIT_DEBIT_CVV": {
                "type": "string",
                "description": "A three-digit card verification code (CVV) present on VISA, MasterCard, and Discover credit and debit cards.",
            }
        },
        "required": ["CREDIT_DEBIT_CVV"],
    }

    CREDIT_DEBIT_EXPIRY = {
        "type": "object",
        "properties": {
            "CREDIT_DEBIT_EXPIRY": {
                "type": "string",
                "description": "The expiration date for a credit or debit card.",
            }
        },
        "required": ["CREDIT_DEBIT_EXPIRY"],
    }

    CREDIT_DEBIT_NUMBER = {
        "type": "object",
        "properties": {
            "CREDIT_DEBIT_NUMBER": {
                "type": "string",
                "description": "The number for a credit or debit card.",
            }
        },
        "required": ["CREDIT_DEBIT_NUMBER"],
    }

    DATE_TIME = {
        "type": "object",
        "properties": {
            "DATE_TIME": {
                "type": "string",
                "description": "A date can include a year, month, day, day of week, or time of day.",
            }
        },
        "required": ["DATE_TIME"],
    }

    DRIVER_ID = {
        "type": "object",
        "properties": {
            "DRIVER_ID": {
                "type": "string",
                "description": "The number assigned to a driver's license.",
            }
        },
        "required": ["DRIVER_ID"],
    }

    EMAIL = {
        "type": "object",
        "properties": {"EMAIL": {"type": "string", "description": "An email address."}},
        "required": ["EMAIL"],
    }

    INTERNATIONAL_BANK_ACCOUNT_NUMBER = {
        "type": "object",
        "properties": {
            "INTERNATIONAL_BANK_ACCOUNT_NUMBER": {
                "type": "string",
                "description": "An International Bank Account Number has specific formats in each country.",
            }
        },
        "required": ["INTERNATIONAL_BANK_ACCOUNT_NUMBER"],
    }

    IP_ADDRESS = {
        "type": "object",
        "properties": {
            "IP_ADDRESS": {"type": "string", "description": "An IPv4 address."}
        },
        "required": ["IP_ADDRESS"],
    }

    LICENSE_PLATE = {
        "type": "object",
        "properties": {
            "LICENSE_PLATE": {
                "type": "string",
                "description": "A license plate for a vehicle.",
            }
        },
        "required": ["LICENSE_PLATE"],
    }

    MAC_ADDRESS = {
        "type": "object",
        "properties": {
            "MAC_ADDRESS": {
                "type": "string",
                "description": "A media access control (MAC) address.",
            }
        },
        "required": ["MAC_ADDRESS"],
    }

    NAME = {
        "type": "object",
        "properties": {
            "NAME": {"type": "string", "description": "An individual's name."}
        },
        "required": ["NAME"],
    }

    PASSWORD = {
        "type": "object",
        "properties": {
            "PASSWORD": {
                "type": "string",
                "description": "An alphanumeric string used as a password.",
            }
        },
        "required": ["PASSWORD"],
    }

    PHONE = {
        "type": "object",
        "properties": {"PHONE": {"type": "string", "description": "A phone number."}},
        "required": ["PHONE"],
    }

    PIN = {
        "type": "object",
        "properties": {
            "PIN": {
                "type": "string",
                "description": "A four-digit personal identification number (PIN).",
            }
        },
        "required": ["PIN"],
    }

    SWIFT_CODE = {
        "type": "object",
        "properties": {
            "SWIFT_CODE": {"type": "string", "description": "A SWIFT code."}
        },
        "required": ["SWIFT_CODE"],
    }

    URL = {
        "type": "object",
        "properties": {"URL": {"type": "string", "description": "A web address."}},
        "required": ["URL"],
    }

    USERNAME = {
        "type": "object",
        "properties": {
            "USERNAME": {
                "type": "string",
                "description": "A user name that identifies an account.",
            }
        },
        "required": ["USERNAME"],
    }

    VEHICLE_IDENTIFICATION_NUMBER = {
        "type": "object",
        "properties": {
            "VEHICLE_IDENTIFICATION_NUMBER": {
                "type": "string",
                "description": "A Vehicle Identification Number (VIN).",
            }
        },
        "required": ["VEHICLE_IDENTIFICATION_NUMBER"],
    }

    CA_HEALTH_NUMBER = {
        "type": "object",
        "properties": {
            "CA_HEALTH_NUMBER": {
                "type": "string",
                "description": "A Canadian Health Service Number.",
            }
        },
        "required": ["CA_HEALTH_NUMBER"],
    }

    CA_SOCIAL_INSURANCE_NUMBER = {
        "type": "object",
        "properties": {
            "CA_SOCIAL_INSURANCE_NUMBER": {
                "type": "string",
                "description": "A Canadian Social Insurance Number (SIN).",
            }
        },
        "required": ["CA_SOCIAL_INSURANCE_NUMBER"],
    }

    IN_AADHAAR = {
        "type": "object",
        "properties": {
            "IN_AADHAAR": {"type": "string", "description": "An Indian Aadhaar number."}
        },
        "required": ["IN_AADHAAR"],
    }

    IN_NREGA = {
        "type": "object",
        "properties": {
            "IN_NREGA": {
                "type": "string",
                "description": "An Indian National Rural Employment Guarantee Act (NREGA) number.",
            }
        },
        "required": ["IN_NREGA"],
    }

    IN_PERMANENT_ACCOUNT_NUMBER = {
        "type": "object",
        "properties": {
            "IN_PERMANENT_ACCOUNT_NUMBER": {
                "type": "string",
                "description": "An Indian Permanent Account Number.",
            }
        },
        "required": ["IN_PERMANENT_ACCOUNT_NUMBER"],
    }

    IN_VOTER_NUMBER = {
        "type": "object",
        "properties": {
            "IN_VOTER_NUMBER": {
                "type": "string",
                "description": "An Indian Voter ID number.",
            }
        },
        "required": ["IN_VOTER_NUMBER"],
    }

    UK_NATIONAL_HEALTH_SERVICE_NUMBER = {
        "type": "object",
        "properties": {
            "UK_NATIONAL_HEALTH_SERVICE_NUMBER": {
                "type": "string",
                "description": "A UK National Health Service Number.",
            }
        },
        "required": ["UK_NATIONAL_HEALTH_SERVICE_NUMBER"],
    }

    UK_NATIONAL_INSURANCE_NUMBER = {
        "type": "object",
        "properties": {
            "UK_NATIONAL_INSURANCE_NUMBER": {
                "type": "string",
                "description": "A UK National Insurance Number (NINO).",
            }
        },
        "required": ["UK_NATIONAL_INSURANCE_NUMBER"],
    }

    UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER = {
        "type": "object",
        "properties": {
            "UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER": {
                "type": "string",
                "description": "A UK Unique Taxpayer Reference (UTR) is a 10-digit number that identifies a taxpayer or a business.",
            }
        },
        "required": ["UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER"],
    }

    BANK_ACCOUNT_NUMBER = {
        "type": "object",
        "properties": {
            "BANK_ACCOUNT_NUMBER": {
                "type": "string",
                "description": "A US bank account number, typically 10 to 12 digits long.",
            }
        },
        "required": ["BANK_ACCOUNT_NUMBER"],
    }

    BANK_ROUTING = {
        "type": "object",
        "properties": {
            "BANK_ROUTING": {
                "type": "string",
                "description": "A US bank routing number, typically nine digits long.",
            }
        },
        "required": ["BANK_ROUTING"],
    }

    PASSPORT_NUMBER = {
        "type": "object",
        "properties": {
            "PASSPORT_NUMBER": {
                "type": "string",
                "description": "A passport number, ranging from six to nine alphanumeric characters.",
            }
        },
        "required": ["PASSPORT_NUMBER"],
    }

    US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER = {
        "type": "object",
        "properties": {
            "US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER": {
                "type": "string",
                "description": "A US Individual Taxpayer Identification Number (ITIN) is a nine-digit number.",
            }
        },
        "required": ["US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER"],
    }

    SSN = {
        "type": "object",
        "properties": {
            "SSN": {
                "type": "string",
                "description": "A US Social Security Number (SSN) is a nine-digit number.",
            }
        },
        "required": ["SSN"],
    }

    ES_NIF = {
        "type": "object",
        "properties": {
            "ES_NIF": {
                "type": "string",
                "description": "A spanish NIF number (Personal tax ID).",
            }
        },
        "required": ["ES_NIF"],
    }

    IT_VAT_CODE = {
        "type": "object",
        "properties": {
            "IT_VAT_CODE": {
                "type": "string",
                "description": "An Italian VAT code number",
            }
        },
        "required": ["IT_VAT_CODE"],
    }

    PL_PESEL_NUMBER = {
        "type": "object",
        "properties": {
            "PL_PESEL_NUMBER": {"type": "string", "description": "Polish PESEL number"}
        },
        "required": ["PL_PESEL_NUMBER"],
    }

    SG_NRIC_FIN = {
        "type": "object",
        "properties": {
            "SG_NRIC_FIN": {
                "type": "string",
                "description": "A National Registration Identification Card",
            }
        },
        "required": ["SG_NRIC_FIN"],
    }

    AU_BUSINESS_NUMBER = {
        "type": "object",
        "properties": {
            "AU_BUSINESS_NUMBER": {
                "type": "string",
                "description": "The Australian Business Number (ABN) is a unique 11 digit identifier issued to all entities registered in the Australian Business Register (ABR).",
            }
        },
        "required": ["AU_BUSINESS_NUMBER"],
    }

    AU_COMPANY_NUMBER = {
        "type": "object",
        "properties": {
            "AU_COMPANY_NUMBER": {
                "type": "string",
                "description": "An Australian Company Number is a unique nine-digit number issued by the Australian Securities and Investments Commission to every company registered under the Commonwealth Corporations Act 2001 as an identifier.",
            }
        },
        "required": ["AU_COMPANY_NUMBER"],
    }

    AU_TAX_FILE_NUMBER = {
        "type": "object",
        "properties": {
            "AU_TAX_FILE_NUMBER": {
                "type": "string",
                "description": "The tax file number (TFN) is a unique identifier issued by the Australian Taxation Office to each taxpaying entity",
            }
        },
        "required": ["AU_TAX_FILE_NUMBER"],
    }

    AU_MEDICARE = {
        "type": "object",
        "properties": {
            "AU_MEDICARE": {
                "type": "string",
                "description": "Medicare number is a unique identifier issued by Australian Government",
            }
        },
        "required": ["AU_MEDICARE"],
    }

    COMMERCIAL_ITEM = {
        "type": "object",
        "properties": {
            "COMMERCIAL_ITEM": {"type": "string", "description": "A branded product."}
        },
        "required": ["COMMERCIAL_ITEM"],
    }

    EVENT = {
        "type": "object",
        "properties": {
            "EVENT": {
                "type": "string",
                "description": "An event, such as a festival, concert, election, etc.",
            }
        },
        "required": ["EVENT"],
    }

    ORGANIZATION = {
        "type": "object",
        "properties": {
            "ORGANIZATION": {
                "type": "string",
                "description": "Large organizations, such as a government, company, religion, sports team, etc.",
            }
        },
        "required": ["ORGANIZATION"],
    }

    PERSON = {
        "type": "object",
        "properties": {
            "PERSON": {
                "type": "string",
                "description": "Individuals, groups of people, nicknames, fictional characters.",
            }
        },
        "required": ["PERSON"],
    }

    QUANTITY = {
        "type": "object",
        "properties": {
            "QUANTITY": {
                "type": "string",
                "description": "A quantified amount, such as currency, percentages, numbers, bytes, etc.",
            }
        },
        "required": ["QUANTITY"],
    }

    TITLE = {
        "type": "object",
        "properties": {
            "TITLE": {
                "type": "string",
                "description": "An official name given to any creation or creative work, such as movies, books, songs, etc.",
            }
        },
        "required": ["TITLE"],
    }
