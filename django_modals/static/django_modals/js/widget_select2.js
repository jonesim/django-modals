var select2_widget = function() {

    function add_CSRF(xhr) {
        xhr.setRequestHeader("X-CSRFToken", ajax_helpers.getCookie("csrftoken"));
    }

    function modal(modal_url) {

        django_modal.show_modal(modal_url);
    }

    function initselect2(select_id, ajax, tags, data, placeholder) {
        var select_element = $("#" + select_id);
        var modal_container = select_element.closest(".modal-content");
        if (modal_container.length === 0) {
            modal_container = $(document.body);
        }
        var modal_url = django_modal.modal_div().attr("data-url");
        var select2_params = {
            theme: "bootstrap4",
            dropdownParent: modal_container,
            allowClear: true,
            placeholder: placeholder
        };

        if (data !== undefined) {
            select2_params.data = data;
        }

        if (data !== undefined || ajax) {
            select2_params.templateSelection = function (text) {
                return $("<span>" + text.text + "</span>");
            };
            select2_params.templateResult = function (text) {
                return $("<span>" + text.text + "</span>");
            };
            select2_params.escapeMarkup = function (text) {
                return text;
            };
        }

        if (tags.enabled) {
            select2_params.tags = true;
            select2_params.createTag = function (params) {
                var term = $.trim(params.term);
                if (term === "") {
                    return null;
                }
                return {
                    id: tags.new_marker + term,
                    text: term
                };
            };
        }
        if (ajax) {
            select2_params.ajax = {
                method: "POST",
                url: modal_url,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", ajax_helpers.getCookie("csrftoken"));
                },
                cache: false,
                contentType: "application/json",
                data: function (params) {
                    var ajax_data = {};
                    $($("#" + select_id).closest("form")).serializeArray().map(function (x) {
                        ajax_data[x.name] = x.value;
                    });
                    ajax_data.select2 = select_id.substring(3);
                    ajax_data.search = params.term;
                    ajax_data.page = params.page || 1;
                    return JSON.stringify(ajax_data);
                }
            };
        }
        select_element.select2(select2_params);
        $(".select2-selection__rendered").hover(function () {
            $(this).removeAttr("title");
        });
    }
    return {
    	initselect2: initselect2,
    	modal: modal
    };
}();
