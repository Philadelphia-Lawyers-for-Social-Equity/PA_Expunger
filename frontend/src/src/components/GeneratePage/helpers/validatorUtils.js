/**
 * 
 * @param {*} input to be validated (note that any number returns true)
 * @returns boolean
 */
function defaultValidator(input) {
    if (typeof input === 'number') {
        return true
    } else {
        return !!input
    }
}

export const addressValidators = {
    street1: {
        validator: defaultValidator,
    },
    city: {
        validator: defaultValidator,
    },
    state: {
        validator:
            (state) => (/^[a-zA-Z]{2}$/).test(state),
    },
    zipcode: {
        validator:
            (zipcode) => (/^\d{5}(-\d{4})?(?!-)$/).test(zipcode),
    },
};

export const requiredInputValidators = {
    petitioner: {
        name: {
            validator: defaultValidator,
            description: 'name',
        },
        dob: {
            validator: defaultValidator,
            description: 'date of birth',
        },
        ssn: {
            validator:
                (ssn = '') => {
                    const hasDashes = /(-)/.test(ssn);
                    return hasDashes ? ssn.length === 11 : ssn.length === 9
                },
            description: 'Social Security number',
        },
        address: {
            validator: 
                (address) => {
                    const keysExpected = Object.keys(addressValidators);
                    for (const key of keysExpected) {
                        if (
                            !address[key] ||
                            !addressValidators[key].validator(address[key])
                        ) return false;
                    }
                    return true;
                },
            description: 'address',
        }
    },
    petition: {
        otn: {
            validator: defaultValidator,
            description: 'Offense Tracking number',
        },
        complaint_date: {
            validator: defaultValidator,
            description: 'complaint date',
        },
        arrest_agency: {
            validator: defaultValidator,
            description: 'arrest agency',
        },
        judge: {
            validator: defaultValidator,
            description: 'judge',
        },
        ratio: {
            validator: defaultValidator,
            description: 'full or partial expungement',
        },
    },
    dockets: {
        validator:
            (dockets) => {
                if (!dockets.length) return false;
                return dockets.every(docket => docket.length);
            },
        description: 'dockets',
    },
    charges: {
        validator:
            (charges, expectedItems) => {
                if (!charges.length) return false;
                for (const item of expectedItems) {
                    const isPresentInAllCharges = charges.every(charge => charge[item]);
                    if (!isPresentInAllCharges) return false
                };
                return true;
            },
        description: 'charges',
    },
    restitution: {
        total: {
            validator: defaultValidator,
            description: 'total restitution',
        },
        paid: {
            validator: defaultValidator,
            description: 'paid restitution',
        }
    }
};

/**
 * 
 * @param {*} formSectionKey Key of section, i.e. 'petitioner' or 'dockets'
 * @param {*} sectionDataSubmitted Submitted data, per section, to be validated
 * @returns If valid, returns an empty array. If invalid, returns an array with a single object
 * whose key is the formSectionKey and whose value is an array of invalid/missing input
 * descriptions (as strings).
 */
export function validateSubmission(formSectionKey, sectionDataSubmitted) {
    if (Array.isArray(sectionDataSubmitted)) {
        const isValid = requiredInputValidators[formSectionKey].validator(sectionDataSubmitted)
        return isValid ? [] : [{ [formSectionKey]: [requiredInputValidators[formSectionKey].description] }]
    } else {
        const keysOfRequiredData = Object.keys(requiredInputValidators[formSectionKey]);
        const sectionErrors = [];
        for (const key of keysOfRequiredData) {
            if (
                !sectionDataSubmitted[key] ||
                !requiredInputValidators[formSectionKey][key].validator(sectionDataSubmitted[key])
            ) {
                sectionErrors.push(requiredInputValidators[formSectionKey][key].description)
            }
        }
        return sectionErrors.length ? [{ [formSectionKey]: sectionErrors}] : []
    }
}