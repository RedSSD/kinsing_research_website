document.addEventListener('DOMContentLoaded', function() {
    const addHeaderButton = document.getElementById('add-header');
    const headersContainer = document.getElementById('button-container');
    const customHeadersInput = document.getElementById('id_custom_headers');

    addHeaderButton.addEventListener('click', function() {
        let values = valuesJson;
        const headerRow = document.createElement('div');
        headerRow.classList.add('header-row');

        const fieldInput = document.createElement('input');
        fieldInput.setAttribute('type', 'text');
        fieldInput.setAttribute('placeholder', 'Field name');
        fieldInput.classList.add('vTextField');

        const selectList = document.createElement('select');
        selectList.classList.add('vTextField');

        for (let value of values) {
            let option = document.createElement('option')
            option.value = value;
            option.textContent = value
            selectList.appendChild(option)
        }
        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.textContent = 'Remove';
        removeButton.classList.add('button', 'deletelink');
        removeButton.addEventListener('click', function() {
            headersContainer.removeChild(headerRow);
            updateCustomHeaders();
        });

        headerRow.appendChild(fieldInput);
        headerRow.appendChild(selectList);
        headerRow.appendChild(removeButton);
        headersContainer.appendChild(headerRow);
        updateCustomHeaders();
    });

    const updateCustomHeaders = function() {
        const headers = {};
        document.querySelectorAll('.header-row').forEach(function(row) {
            const field = row.querySelector('input[type="text"]:nth-child(1)').value.trim();
            const header = row.querySelector('select').value.trim();
            if (field && header) {
                headers[field] = header;
            }
        });
        customHeadersInput.value = JSON.stringify(headers);
    };

    headersContainer.addEventListener('change', updateCustomHeaders);
});
