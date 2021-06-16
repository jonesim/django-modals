/*
    Displays stacked modals with increasing z-index and backdrop
    Processes response from View which can be either

        1. html to redisplay
        2. json commands to process
        3. file attachment to download

    modals contained in <div> with id modal-%no% which is created initially and destroyed on hidden
*/
if (typeof modal == 'undefined') {
    var modal = function () {
        let window_width = 1022
        var open_modals = 0;
        var modals = []
        var process_lock = false;
        var post_load_event = new CustomEvent('modalPostLoad');
        var target;

        ajax_helpers.command_functions.reload = function () {
            if (open_modals > 1) {
                ajax_helpers.command_functions.close()
            } else {
                if (determine_type() != 'popup') {
                    ajax_helpers.ajax_busy = true
                    location.reload();
                } else {
                    window.opener.postMessage({commands: [{function: 'reload'},], initurl: target}, target);
                    window.close();
                }
            }
        }

        ajax_helpers.command_functions.close = function (command) {
            if (command !== undefined && command.no_refresh === true){
                modals[modals.length-1].no_refresh = true
            }
            if (determine_type() == 'popup') {
                window.close()
            } else {
                ajax_helpers.ajax_busy = true;
                modal_div().modal('hide');
            }
        }
        ajax_helpers.command_functions.overwrite_modal = function (command) {
            if (command.selector === undefined){
                command.selector = '#' + modal.active_modal_container_id()
            }
            ajax_helpers.command_functions.html(command)
            init_modal_container($(command.selector))
        }
        ajax_helpers.command_functions.show_modal = function (command) {
            ajax_helpers.ajax_busy = true;
            show_modal(command.modal);
        }
        ajax_helpers.command_functions.modal_html = function (command) {
            create_modal(command.html);
        }
        ajax_helpers.command_functions.post_modal = function (command) {
            send_inputs(command.button);
        }

        ajax_helpers.command_functions.modal_refresh_trigger = function (command) {
            $(command.selector).trigger('modalPostLoad', [modal.active_modal_container_id()])
        }

        if (window.opener != null) {
            target = window.opener.location.href
        }


        function determine_type() {
            if (typeof (form_url) == 'undefined') {
                    return 'modal'
            } else {
                switch (open_modals) {
                    case 1:
                        return 'popup'
                    default:
                        return 'modal'
                }
            }
        }

        function create_modal(modal_html) {
            open_modals += 1;
            modals.push({id: active_modal_container_id()})
            modal_container = $('<div>', {id: active_modal_container_id()}).appendTo('body');
            modal_container.html(modal_html);
            if (open_modals === 1) {
                backdrop = $('<div>', {class: 'modal-backdrop fade'}).appendTo('body');
                window.setTimeout(function () {
                    $(backdrop).addClass('show')
                }, 50)
            }
            set_backdrop_z();
            init_modal_container(modal_container)
            /*
            window.onbeforeunload = function() {
                if (open_modals > 0){
                       return "Do you really want to leave our brilliant application?";
                }
            };
            */
        }
        function init_modal_container(modal_container){
            modal_element = modal_container.children();
            modal_element.css('z-index', 1040 + (10 * open_modals));
            modal_element.modal({'backdrop': false})
            modal_type = determine_type();
            modal_element.on('hidden.bs.modal', function (event) {
                $(this).parent().remove();
                open_modals -= 1;
                if (open_modals == 0){
                    $('.modal-backdrop').remove()
                }
                var closing_modal = modals.pop()
                set_backdrop_z();
                open_modals && $(document.body).addClass('modal-open');
                ajax_helpers.ajax_busy = false;
                if (open_modals > 0 && closing_modal.no_refresh !== true) {
                    send_inputs('refresh_form')
                }
            });
            modal_element.on('shown.bs.modal', function (event) {
                ajax_helpers.ajax_busy = false;
            });

            $('form input').keydown(function (e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
                    $('.modal-submit')[0].click()
                    return false;
                }
            });
            // modalPostLoad used to configure datepicker/select2 etc
            if (determine_type() == 'popup') {
                window.resizeTo(window_width, $(document).height() + window.outerHeight - window.innerHeight)
            }
            modal_container.trigger('modalPostLoad', [active_modal_container_id()])
            //modal_container.draggable({handle: ".modal-header"});
            if (open_modals > 1 || window.opener == null) {
                $('.modal-dialog').draggable({handle: ".modal-header"});
            }
        }

        function additional_parameters(params) {
            if (typeof (params) == 'undefined') params = {};
            params.modal_id = active_modal_container_id()
            //params.modal_page_url = window.location.pathname;
            //params.modal_querystring = window.location.search;
            return params;
        }

        function process_commands_lock(commands) {
            if (!process_lock && !ajax_helpers.ajax_busy) {
                process_lock = true;
                ajax_helpers.process_commands(commands);
                process_lock = false
            }
        }

        function active_modal_container_id(index) {
            if (typeof (index) == 'undefined') index = 0;
            return 'modal-' + (open_modals + index).toString()
        }

        function get_modal_container(index) {
            return $('#' + active_modal_container_id(index))
        }

        function modal_div(index) {
            return get_modal_container(index).children()
        }

        function set_backdrop_z() {
            $('.modal-backdrop').css('z-index', 1039 + (10 * open_modals));
        }


        function show_modal(modal_url, slug, params) {

            if (typeof slug != 'undefined') {
                ajax_url = modal_url + slug + '/?'
            } else {
                ajax_url = modal_url + '?'
            }

            $.ajax({
                url: ajax_url + $.param(additional_parameters(params)),
            }).done(function (response) {
                create_modal(response);
            })
        }

        function send_inputs(button_name, callback, index) {
            if (typeof (button_name) == 'object') {
                params = button_name
            } else if (typeof (button_name) != 'undefined') {
                params = {'button': button_name}
            } else {
                params = {}
            }
            params = additional_parameters(params);
            modal_container = get_modal_container(index);
            modal_url = modal_container.find("input[name='modal_name']").val();
            if (typeof callback != 'undefined') {
                modal_url = url_change(modal_url, 'modalstyle', 'windowform')
            }
            if (typeof (tinymce) != 'undefined') tinymce.triggerSave();

            forms = modal_container.find('form')
            if (forms.length > 1) {
                var data = {}
                for (var f of forms) {
                    var form_data = new FormData(f)
                    data[f.id] = {}
                    for (var d of form_data.entries()) {
                        data[f.id][d[0]] = d[1]
                    }
                }
                data = (JSON.stringify(data))
            } else {
                data = new FormData(forms[0])
                for (var property in params) {
                    data.append(property, params[property])
                }
            }
            ajax_helpers.post_data(modal_url, data)
        }

        function url_change(url, key, value) {
            split_url = url.split('/')
            var slug = split_url[split_url.length - 2]
            var split_slug = slug.split('-')
            if (split_slug.length == 1) {
                split_slug = ['pk', slug]
            }
            split_slug.push(key)
            split_slug.push(value)
            split_url[split_url.length - 2] = split_slug.join('-')
            return split_url.join('/')
        }

        function process_event(event) {
            if (open_modals == 0 && window.location.href == event.data.initurl) {
                process_commands(event.data.commands)
            }
        }
        window.addEventListener("message", process_event)
        function load_external_modal(document, html) {
            if (typeof document.modal == 'undefined') {
                window.setTimeout(function () {
                    load_external_modal(document, html)
                }, 100)
            } else {
                doc.modal.create_modal(html)
            }
        }

        function minimise(button) {

            modal_container = get_modal_container();
            modal_name = modal_container.find("input[name='modal_name']").val();
            modal_name = url_change(modal_name, 'modalstyle', 'window')
            doc = window.open(modal_name, "", "width=" + window_width + ",height=20")
            ajax_helpers.command_functions.close()
            send_inputs('refresh_form', function (form_response) {
                load_external_modal(doc, form_response)
            })
            //modal_container = get_modal_container();
            //modal_name = modal_container.find("input[name='modal_name']").val();
            //window.open('/modal/' + modal_name + '/', width=600, height=400 )
            //  modal_div().toggleClass('minimised')
            //   $('.modal-backdrop').toggle();
            //    $('body').removeClass('modal-open')
            //   modal_div().hide()
        }
        return {
            show_modal,
            send_inputs,
            minimise,
            create_modal,
            process_commands_lock,
            active_modal_container_id,
        }
    }();
}
