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
        var modal_busy = false;
        var process_lock = false;
        var post_load_event = new CustomEvent('modalPostLoad');
        var target;

        if (window.opener != null) {
            target = window.opener.location.href
        }


        function determine_type() {
            if (typeof(form_url)=='undefined'){
                if (open_modals == 1) {
                    return 'modal_base'
                } else {
                    return 'modal'
                }
            } else {
                switch (open_modals) {
                    case 1:
                        return 'popup'
                    case 2:
                        return 'modal_base'
                    default:
                        return 'modal'
                }
            }
        }

        function create_modal(modal_html) {
            open_modals += 1;
            modal_container = $('<div>', {id: active_modal_container_id()}).appendTo('body');
            modal_container.html(modal_html);

            /*
            window.onbeforeunload = function() {
                if (open_modals > 0){
                       return "Do you really want to leave our brilliant application?";
                }
            };
            */
            modal_element = modal_container.children();
            modal_element.css('z-index', 1040 + (10 * open_modals));

            modal_type = determine_type();
            switch (modal_type) {
                case 'modal_base':
                    modal_element.modal();
                    set_backdrop_z();
                    break;
                case 'modal':
                    modal_element.modal({'backdrop': false});
                    set_backdrop_z();
                    break;
            }

            modal_element.on('hidden.bs.modal', function (event) {
                $(this).parent().remove();
                open_modals -= 1;
                set_backdrop_z();
                open_modals && $(document.body).addClass('modal-open');
                modal_busy = false;
                if (open_modals > 0) {
                    send_inputs('refresh_form')
                }
            });
            modal_element.on('shown.bs.modal', function (event) {
                modal_busy = false;
            });

            $('form input').keydown(function (e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
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
            //params.modal_page_url = window.location.pathname;
            //params.modal_querystring = window.location.search;
            return params;
        }

        function process_commands(commands) {
            if (modal_busy) {
                window.setTimeout(function () {
                    process_commands(commands)
                }, 100)
            } else {
                while (commands.length > 0) {
                    command = commands.shift()
                    modal_functions[command.function](command);
                    if (modal_busy) {
                        window.setTimeout(function () {
                            process_commands(commands)
                        }, 100)
                        break;
                    }
                }
            }
        }

        function process_commands_lock(commands) {
            if (!process_lock && !modal_busy){
                process_lock = true;
                process_commands(commands);
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


        modal_functions = {
            close: function () {
                if (determine_type() == 'popup'){
                    window.close()
                } else {
                    modal_busy = true;
                    modal_div().modal('hide');
                }
            },
            reload: function () {
//            modal_name = modal_container.find("input[name='modal_style']").val();
                if (open_modals > 1) {
                    modal_functions.close()
                } else {
                    if (determine_type()!='popup') {
                        modal_busy = true
                        location.reload();
                    } else {
                        window.opener.postMessage({commands: [{function:'reload'},], initurl: target}, target);
                        window.close();
                    }
                }
            },
            redirect: function () {
                window.location.href = command.url;
            },
            show_modal: function (command) {
                modal_busy = true;
                show_modal(command.modal);
            },
            post_modal: function (command) {
                send_inputs(command.button_name);
            },
            modal_html: function (command) {
                create_modal(command.html);
            },
        };

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
                params = {'button_name': button_name}
            } else {
                params = {}
            }
            params = additional_parameters(params);
            modal_container = get_modal_container(index);
            modal_url = modal_container.find("input[name='modal_name']").val();
            if (typeof callback != 'undefined') {
                modal_url = url_change(modal_url, 'modalstyle', 'windowform')
            }
            if (typeof(tinymce)!='undefined') tinymce.triggerSave();
            data = new FormData(modal_container.find('form')[0])
            for (var property in params) {
                data.append(property, params[property])
            }
            post_data(modal_url, data, modal_div(), callback)
/*
            $.ajax(
                {
                    url: modal_name,
                    method: 'post',
                    data: data,
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    },
                    cache: false,
                    contentType: false,
                    processData: false,

                    success: function (form_response, status, jqXHR) {
                        content_disposition = jqXHR.getResponseHeader('Content-Disposition')
                        if (typeof (content_disposition) == 'string' && content_disposition.indexOf('attachment') > -1) {
                            blob = new Blob([form_response], {type: "octet/stream"})
                            url = window.URL.createObjectURL(blob);
                            a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = content_disposition.split('"')[1];
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            alert('your file has downloaded');
                        } else if (typeof (form_response) == 'object') {
                            process_commands(form_response)
                        } else if (typeof callback != 'undefined') {
                            callback(form_response)
                        } else {
                            //org_pos = $(modal_div().find('.modal-dialog')[0]).position()
                            //org_pos['top'] = org_pos['top'] + modal_div().scrollTop()
                            modal_div().html($(form_response).html())
                            //$(modal_div().find('.modal-dialog')[0]).css(org_pos)
                            modal_div().trigger('modalPostLoad', [active_modal_container_id()])
                        }
                    }
                })

 */
        }

        function send_form(url, form_id, extra_data){
            if (form_id != null){
                form = $('#' + form_id)
                data = new FormData(form[0])
                parent = $(form.parent()[0])
            }
            else{
                data = new FormData()
                parent = null
            }
            if (typeof(extra_data) != 'undefined')
            {
                for (var property in extra_data) {
                    data.append(property, extra_data[property])
                }
            }
            post_data(url, data, parent)
        }

        function post_data(url, data, form_div, callback){

           $.ajax(
                {
                    url: url,
                    method: 'post',
                    data: data,
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    },
                    cache: false,
                    contentType: false,
                    processData: false,

                    success: function (form_response, status, jqXHR) {
                        content_disposition = jqXHR.getResponseHeader('Content-Disposition')
                        if (typeof (content_disposition) == 'string' && content_disposition.indexOf('attachment') > -1) {
                            blob = new Blob([form_response], {type: "octet/stream"})
                            download_url = window.URL.createObjectURL(blob);
                            a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = download_url;
                            a.download = content_disposition.split('"')[1];
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(download_url);
                            alert('your file has downloaded');
                        } else if (typeof (form_response) == 'object') {
                            process_commands(form_response)
                        } else if (typeof callback != 'undefined') {
                            callback(form_response)
                        } else {
                            if ($(form_response).hasClass('modal')){
                                form_div.html($(form_response).html())
                            }
                            else{
                                form_div.html($(form_response))
                            }
                            form_div.trigger('modalPostLoad', [active_modal_container_id()])
                        }
                    }
                })

        }

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }


        function url_change(url, key, value) {
            split_url = url.split('/')
            slug = split_url[split_url.length - 2]
            split_slug = slug.split('-')
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
            doc = window.open(modal_name, "", "width="+ window_width + ",height=20")
            modal_functions.close()
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
            modal_functions,
            show_modal,
            send_inputs,
            process_commands,
            minimise,
            create_modal,
            getCookie,
            send_form,
            process_commands_lock,
        }

    }();
}
