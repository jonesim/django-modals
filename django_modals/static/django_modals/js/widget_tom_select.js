var tom_select_widget = function () {

    function strip_id(org_id) {
        if (org_id.substring(0, 3) === 'id_') {
            return org_id.substring(3);
        }
        return org_id;
    }

    // Build the POST body in exactly the same shape widget_select2.js sends, so the server-side
    // select2_<field> / select2_ajax_search handlers are reused unchanged.
    function build_post_data(select_id, field_name, search, page) {
        var ajax_data = {};
        var raw_values = {};
        $($("#" + select_id).closest("form")).serializeArray().map(function (x) {
            ajax_data[x.name] = x.value;
            if (!raw_values.hasOwnProperty(x.name)) {
                raw_values[x.name] = [x.value];
            } else {
                raw_values[x.name].push(x.value);
            }
        });
        ajax_data.raw_values = raw_values;
        ajax_data.select2 = field_name;
        ajax_data.search = search;
        ajax_data.page = page;
        return ajax_data;
    }

    function post_search(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // AjaxHelpers.post only routes the select2 key when is_ajax() sees this header
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': ajax_helpers.getCookie('csrftoken')
            },
            cache: 'no-store',
            body: JSON.stringify(body)
        }).then(function (response) {
            return response.json();
        });
    }

    function inittomselect(select_id, ajax, tags, data, placeholder, html_template, html_result_template,
                           selected_ajax, cleared_ajax) {
        // A custom dropdown (option) template falls back to the selection (item) template, matching
        // select2's templateResult/templateSelection. When neither is supplied we leave Tom Select's
        // own block renderers in place (overriding with an inline <span> made the options flow
        // horizontally instead of stacking as rows).
        if (html_result_template === undefined) {
            html_result_template = html_template;
        }

        var field_name = strip_id(select_id);
        var modal_url = django_modal.modal_div().attr("data-url");

        var select_element;
        if (django_modal.active_modal_container_id() != 'modal-0') {
            select_element = $("#" + select_id, '#' + django_modal.active_modal_container_id())[0];
        } else {
            select_element = $("#" + select_id)[0];
        }
        if (!select_element) {
            return;
        }

        // The field renderer tags the <select> with Bootstrap's `custom-select`, and Tom Select
        // copies the element's class attribute onto its generated `.ts-wrapper`. That would paint
        // Bootstrap's own chevron/appearance on top of the Tom Select control, so strip it first
        // (the original <select> is hidden after init, so removing it there has no visible effect).
        select_element.classList.remove('custom-select');

        var settings = {
            valueField: 'id',
            labelField: 'text',
            searchField: 'text',
            allowEmptyOption: true,
            placeholder: placeholder,
            plugins: ['clear_button']
        };

        if (data !== undefined) {
            settings.options = data;
        }

        // Mirror select2's templateResult / templateSelection, but only when a custom template was
        // actually supplied -- otherwise Tom Select's default block renderers are used. The option
        // output is wrapped in a <div> so each result stacks as its own row (custom templates often
        // return inline <span>s, which would otherwise flow horizontally).
        settings.render = {};
        if (html_result_template !== undefined) {
            settings.render.option = function (item, escape) {
                return '<div>' + html_result_template(item) + '</div>';
            };
        }
        if (html_template !== undefined) {
            settings.render.item = function (item, escape) {
                return html_template(item);
            };
        }

        if (tags.enabled) {
            settings.create = function (input) {
                var term = $.trim(input);
                if (term === "") {
                    return false;
                }
                return {id: tags.new_marker + term, text: term};
            };
            settings.createFilter = function (input) {
                return $.trim(input) !== "";
            };
        }

        if (ajax) {
            settings.plugins.push('virtual_scroll');
            settings.preload = 'focus';
            settings.loadThrottle = 300;
            settings.shouldLoad = function () {
                return true;
            };
            // The virtual_scroll plugin uses getUrl()/setNextUrl() to carry a paging token between
            // loads; here that token is simply the next page number (firstUrl seeds page 1).
            settings.firstUrl = function (query) {
                return 1;
            };
            settings.load = function (query, callback) {
                var self = this;
                var page = parseInt(self.getUrl(query), 10) || 1;
                post_search(modal_url, build_post_data(select_id, field_name, query, page)).then(function (json) {
                    if (json.pagination && json.pagination.more) {
                        self.setNextUrl(query, page + 1);
                    }
                    callback(json.results);
                }).catch(function () {
                    callback();
                });
            };
        }

        var control = new TomSelect(select_element, settings);

        // selected / cleared callbacks -- same routing keys (<field>_selected / <field>_cleared)
        // and same delivery modes (true -> post_json, 'form' -> send the whole form) as select2.
        if (selected_ajax === true) {
            control.on('item_add', function () {
                ajax_helpers.post_json({
                    data: {
                        select2: field_name + '_selected',
                        data: control.getValue()
                    }
                });
            });
        } else if (selected_ajax === 'form') {
            control.on('item_add', function () {
                django_modal.send_inputs({select2: field_name + '_selected'});
            });
        }
        if (cleared_ajax === true) {
            control.on('clear', function () {
                ajax_helpers.post_json({
                    data: {
                        select2: field_name + '_cleared',
                        data: control.getValue()
                    }
                });
            });
        } else if (cleared_ajax === 'form') {
            control.on('clear', function () {
                django_modal.send_inputs({select2: field_name + '_cleared'});
            });
        }
        return control;
    }

    return {
        inittomselect: inittomselect
    };
}();
