Named Entity Recognition (NER)
==============================

Rhubarb comes with 50 built-in entities which includes common entities such as :code:`LOCATION`, :code:`EVENT` etc. Entities 
are available via the :code:`Entities` class. You can pick and choose which entities to detect and then pass them onto the 
:code:`run_entity()` method.

.. code:: python
   :emphasize-lines: 6,7

     from rhubarb import DocAnalysis, Entities

     da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                    boto3_session=session,
                    pages=[1,3])
     resp = da.run_entity(message="Extract all the specified entities from this document.", 
                          entities=[Entities.PERSON, Entities.ADDRESS])

Sample response

.. code-block:: json

    {
        "output": [
            {
                "page": 1,
                "entities": [
                    {"PERSON": "Martha C Rivera"},
                    {"ADDRESS": "8 Any Plaza, 21 Street, Any City, CA 90210"}
                ]
            },
            {
                "page": 3,
                "entities": [
                    {"PERSON": "Mateo Rivera"},
                    {"PERSON": "Pat Rivera"},
                    {"ADDRESS": "8 Any Plaza, 21 Street, Any City, CA 90210"}
                ]
            }
        ],
        "token_usage": {
            "input_tokens": 3531,
            "output_tokens": 168
        }
    }


Supported Entities
------------------

Below is a list of entities that are supported.

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Entity
     - Description
   * - :code:`Entities.ADDRESS`
     - A physical address, such as '100 Main Street, Anytown, USA' or 'Suite #12, Building 123'.
   * - :code:`Entities.AGE`
     - An individual's age, including the quantity and unit of time.
   * - :code:`Entities.AWS_ACCESS_KEY`
     - A unique identifier that's associated with a secret access key; used to sign programmatic AWS requests cryptographically.
   * - :code:`Entities.AWS_SECRET_KEY`
     - A unique identifier that's associated with an access key.
   * - :code:`Entities.CREDIT_DEBIT_CVV`
     - A three-digit card verification code (CVV) present on VISA, MasterCard, and Discover credit and debit cards.
   * - :code:`Entities.CREDIT_DEBIT_EXPIRY`
     - The expiration date for a credit or debit card.
   * - :code:`Entities.CREDIT_DEBIT_NUMBER`
     - The number for a credit or debit card.
   * - :code:`Entities.DATE_TIME`
     - A date can include a year, month, day, day of week, or time of day.
   * - :code:`Entities.DRIVER_ID`
     - The number assigned to a driver's license.
   * - :code:`Entities.EMAIL`
     - An email address.
   * - :code:`Entities.INTERNATIONAL_BANK_ACCOUNT_NUMBER`
     - An International Bank Account Number has specific formats in each country.
   * - :code:`Entities.IP_ADDRESS`
     - An IPv4 address.
   * - :code:`Entities.LICENSE_PLATE`
     - A license plate for a vehicle.
   * - :code:`Entities.MAC_ADDRESS`
     - A media access control (MAC) address.
   * - :code:`Entities.NAME`
     - An individual's name.
   * - :code:`Entities.PASSWORD`
     - An alphanumeric string used as a password.
   * - :code:`Entities.PHONE`
     - A phone number.
   * - :code:`Entities.PIN`
     - A four-digit personal identification number (PIN).
   * - :code:`Entities.SWIFT_CODE`
     - A SWIFT code.
   * - :code:`Entities.URL`
     - A web address.
   * - :code:`Entities.USERNAME`
     - A user name that identifies an account.
   * - :code:`Entities.VEHICLE_IDENTIFICATION_NUMBER`
     - A Vehicle Identification Number (VIN).
   * - :code:`Entities.CA_HEALTH_NUMBER`
     - A Canadian Health Service Number.
   * - :code:`Entities.CA_SOCIAL_INSURANCE_NUMBER`
     - A Canadian Social Insurance Number (SIN).
   * - :code:`Entities.IN_AADHAAR`
     - An Indian Aadhaar number.
   * - :code:`Entities.IN_NREGA`
     - An Indian National Rural Employment Guarantee Act (NREGA) number.
   * - :code:`Entities.IN_PERMANENT_ACCOUNT_NUMBER`
     - An Indian Permanent Account Number.
   * - :code:`Entities.IN_VOTER_NUMBER`
     - An Indian Voter ID number.
   * - :code:`Entities.UK_NATIONAL_HEALTH_SERVICE_NUMBER`
     - A UK National Health Service Number.
   * - :code:`Entities.UK_NATIONAL_INSURANCE_NUMBER`
     - A UK National Insurance Number (NINO).
   * - :code:`Entities.UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER`
     - A UK Unique Taxpayer Reference (UTR) is a 10-digit number that identifies a taxpayer or a business.
   * - :code:`Entities.BANK_ACCOUNT_NUMBER`
     - A US bank account number, typically 10 to 12 digits long.
   * - :code:`Entities.BANK_ROUTING`
     - A US bank routing number, typically nine digits long.
   * - :code:`Entities.PASSPORT_NUMBER`
     - A passport number, ranging from six to nine alphanumeric characters.
   * - :code:`Entities.US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER`
     - A US Individual Taxpayer Identification Number (ITIN) is a nine-digit number.
   * - :code:`Entities.SSN`
     - A US Social Security Number (SSN) is a nine-digit number.
   * - :code:`Entities.ES_NIF`
     - A Spanish NIF number (Personal tax ID).
   * - :code:`Entities.IT_VAT_CODE`
     - An Italian VAT code number.
   * - :code:`Entities.PL_PESEL_NUMBER`
     - Polish PESEL number.
   * - :code:`Entities.SG_NRIC_FIN`
     - A National Registration Identification Card.
   * - :code:`Entities.AU_BUSINESS_NUMBER`
     - The Australian Business Number (ABN) is a unique 11 digit identifier issued to all entities registered in the Australian Business Register (ABR).
   * - :code:`Entities.AU_COMPANY_NUMBER`
     - An Australian Company Number is a unique nine-digit number issued by the Australian Securities and Investments Commission to every company registered under the Commonwealth Corporations Act 2001 as an identifier.
   * - :code:`Entities.AU_TAX_FILE_NUMBER`
     - The tax file number (TFN) is a unique identifier issued by the Australian Taxation Office to each taxpaying entity.
   * - :code:`Entities.AU_MEDICARE`
     - Medicare number is a unique identifier issued by Australian Government.
   * - :code:`Entities.COMMERCIAL_ITEM`
     - A branded product.
   * - :code:`Entities.EVENT`
     - An event, such as a festival, concert, election, etc.
   * - :code:`Entities.ORGANIZATION`
     - Large organizations, such as a government, company, religion, sports team, etc.
   * - :code:`Entities.PERSON`
     - Individuals, groups of people, nicknames, fictional characters.
   * - :code:`Entities.QUANTITY`
     - A quantified amount, such as currency, percentages, numbers, bytes, etc.
   * - :code:`Entities.TITLE`
     - An official name given to any creation or creative work, such as movies, books, songs, etc.
