document.addEventListener('DOMContentLoaded', function () {
    let brand_select = document.getElementById('id_brand');
    let model_select = document.getElementById('id_model');
    let part_group_select = document.getElementById('id_part_group');
    let part_select = document.getElementById('id_part');
    if (brand_select && part_group_select){
       if(brand_select.value.length === 1){

        let SelectBrand = brand_select.value;
        changeMenu(SelectBrand, model_select, 'brand_id')

        brand_select.addEventListener('change', function () {
            const SelectBrand = this.value;
            changeMenu(SelectBrand, model_select, 'brand_id', true)

            });
        }
        if (brand_select.value.length === 0) {
            brand_select.addEventListener('change', function () {
                const SelectBrand = this.value;
                changeMenu(SelectBrand, model_select, 'brand_id', true);
            });
        }

        if (part_group_select.value.length === 1) {

            let SelectBrand = part_group_select.value;
            changeMenu(SelectBrand, model_select, 'part_group_id')

            part_group_select.addEventListener('change', function () {
                const SelectPartGroup = this.value;
                changeMenu(SelectPartGroup, part_select, 'part_group_id', true);


            });
        }

        if (part_group_select.value.length === 0) {
            part_group_select.addEventListener('change', function () {
                const SelectPartGroup = this.value;
                changeMenu(SelectPartGroup, part_select, 'part_group_id', true);
            });
        }
    }

});

function changeMenu(SelectPartGroup, object_select, key_request, skip=false) {
    fetch('/data_parsin_link/', {
        method: 'POST',
        headers : {
            'Content-type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({[key_request]: SelectPartGroup}),
    })
    .then(response => response.json())
    .then(data => {

        for (let i = 0; i < object_select.options.length; i++) {
            object_select.options[i].style.display = '';
        }

        if (data['data'] !== '----') {
            for (let i = 0; i < object_select.options.length; i++) {
                let OptionValue = object_select.options[i].value;

                let found = false;
                for (let item of data['data']){
                    if (item.toString() === OptionValue) {
                        found = true;
                        break
                    }
                }

                if (!found) {
                    object_select.options[i].style.display = 'none';
                }
                if(skip){
                    object_select.value = '';
                }

            }
        }

    });

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
