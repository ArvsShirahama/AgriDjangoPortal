/**
 * Philippine Address Cascading Selector
 * Loads PSGC normalized data from /static/data/philippines_locations.json
 * Updates Province -> City/Municipality -> Barangay -> Street -> Full Home Address
 */
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        const countrySelect = document.getElementById('addr_country');
        const provinceSelect = document.getElementById('addr_province');
        const citySelect = document.getElementById('addr_city');
        const brgySelect = document.getElementById('addr_barangay');
        const streetInput = document.getElementById('addr_street');
        const addressTextarea = document.getElementById('id_address') || document.querySelector('[name="address"]');

        const wrapperProvince = document.getElementById('wrapper_addr_province');
        const wrapperCity = document.getElementById('wrapper_addr_city');
        const wrapperBrgy = document.getElementById('wrapper_addr_barangay');

        if (!provinceSelect || !citySelect || !brgySelect || !addressTextarea) {
            return;
        }

        let locationsData = null;

        // Fetch normalized Philippine location data
        fetch('/static/data/philippines_locations.json')
            .then(function (res) { return res.json(); })
            .then(function (data) {
                locationsData = data;
                initProvinces();
                tryPrefillFromExisting();
            })
            .catch(function (err) {
                console.error('Failed to load Philippine location data:', err);
            });

        function initProvinces() {
            if (!locationsData) return;
            provinceSelect.innerHTML = '<option value="">Select Province</option>';
            const provinces = Object.keys(locationsData).sort();
            provinces.forEach(function (prov) {
                const opt = document.createElement('option');
                opt.value = prov;
                opt.textContent = prov;
                provinceSelect.appendChild(opt);
            });
        }

        function updateFullAddress() {
            const country = countrySelect ? countrySelect.value : 'Philippines';
            if (country !== 'Philippines') {
                return;
            }

            const street = streetInput ? streetInput.value.trim() : '';
            const brgy = brgySelect ? brgySelect.value.trim() : '';
            const city = citySelect ? citySelect.value.trim() : '';
            const prov = provinceSelect ? provinceSelect.value.trim() : '';

            const parts = [];
            if (street) parts.push(street);
            if (brgy) parts.push('Brgy. ' + brgy);
            if (city) parts.push(city);
            if (prov) parts.push(prov);
            if (country) parts.push(country);

            if (parts.length > 0) {
                addressTextarea.value = parts.join(', ');
            }
        }

        function onProvinceChange() {
            const prov = provinceSelect.value;
            citySelect.innerHTML = '<option value="">Select City / Municipality</option>';
            brgySelect.innerHTML = '<option value="">Select Barangay</option>';
            brgySelect.disabled = true;

            if (prov && locationsData && locationsData[prov]) {
                citySelect.disabled = false;
                const cities = Object.keys(locationsData[prov]).sort();
                cities.forEach(function (city) {
                    const opt = document.createElement('option');
                    opt.value = city;
                    opt.textContent = city;
                    citySelect.appendChild(opt);
                });
            } else {
                citySelect.disabled = true;
            }
            updateFullAddress();
        }

        function onCityChange() {
            const prov = provinceSelect.value;
            const city = citySelect.value;
            brgySelect.innerHTML = '<option value="">Select Barangay</option>';

            if (prov && city && locationsData && locationsData[prov] && locationsData[prov][city]) {
                brgySelect.disabled = false;
                const brgys = locationsData[prov][city];
                brgys.forEach(function (brgy) {
                    const opt = document.createElement('option');
                    opt.value = brgy;
                    opt.textContent = brgy;
                    brgySelect.appendChild(opt);
                });
            } else {
                brgySelect.disabled = true;
            }
            updateFullAddress();
        }

        function onBrgyChange() {
            updateFullAddress();
        }

        function onCountryChange() {
            const country = countrySelect.value;
            const isPh = (country === 'Philippines');
            if (wrapperProvince) wrapperProvince.style.display = isPh ? '' : 'none';
            if (wrapperCity) wrapperCity.style.display = isPh ? '' : 'none';
            if (wrapperBrgy) wrapperBrgy.style.display = isPh ? '' : 'none';

            if (isPh) {
                updateFullAddress();
            } else if (country && country !== 'Other') {
                if (!addressTextarea.value || addressTextarea.value.includes('Philippines')) {
                    addressTextarea.value = country;
                }
            }
        }

        if (countrySelect) countrySelect.addEventListener('change', onCountryChange);
        provinceSelect.addEventListener('change', onProvinceChange);
        citySelect.addEventListener('change', onCityChange);
        brgySelect.addEventListener('change', onBrgyChange);
        if (streetInput) streetInput.addEventListener('input', updateFullAddress);

        function tryPrefillFromExisting() {
            const currentAddr = addressTextarea.value.trim();
            if (!currentAddr || !locationsData) return;

            // Attempt to match province in current address
            const provKeys = Object.keys(locationsData);
            for (let i = 0; i < provKeys.length; i++) {
                const prov = provKeys[i];
                if (currentAddr.toLowerCase().indexOf(prov.toLowerCase()) !== -1) {
                    provinceSelect.value = prov;
                    onProvinceChange();

                    const cities = locationsData[prov];
                    const cityKeys = Object.keys(cities);
                    for (let j = 0; j < cityKeys.length; j++) {
                        const city = cityKeys[j];
                        if (currentAddr.toLowerCase().indexOf(city.toLowerCase()) !== -1) {
                            citySelect.value = city;
                            onCityChange();

                            const brgys = cities[city];
                            for (let k = 0; k < brgys.length; k++) {
                                const brgy = brgys[k];
                                if (currentAddr.toLowerCase().indexOf(brgy.toLowerCase()) !== -1) {
                                    brgySelect.value = brgy;
                                    break;
                                }
                            }
                            break;
                        }
                    }
                    break;
                }
            }
        }
    });
})();
