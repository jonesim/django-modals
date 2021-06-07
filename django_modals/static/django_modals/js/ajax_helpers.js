if (typeof ajax_helpers === 'undefined') {
    var ajax_helpers = function () {

        var window_location = window.location;
        var ajax_busy = false;

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function send_form(form_id, extra_data) {
            var data;
            if (form_id != null) {
                var form = $('#' + form_id);
                data = new FormData(form[0]);
            } else {
                data = new FormData();
            }
            if (extra_data !== 'undefined') {
                for (var property in extra_data) {
                    data.append(property, extra_data[property]);
                }
            }
            ajax_helpers.post_data(ajax_helpers.window_location, data);
        }

        function contains_file(jqXHR) {
            var content_disposition = jqXHR.getResponseHeader('Content-Disposition')
            return typeof (content_disposition) == 'string' && content_disposition.indexOf('attachment') > -1;
        }

        function add_CSRF(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }

        function download_file(jqXHR, response) {
            var content_disposition = jqXHR.getResponseHeader('Content-Disposition')
            var blob = new Blob([response], {type: "octet/stream"})
            var download_url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.style.display = 'none';
            a.href = download_url;
            a.download = content_disposition.split('"')[1];
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(download_url);
            alert('your file has downloaded');
        }

        function post_data(url, data) {
            $.ajax(
                {
                    url: url,
                    method: 'post',
                    data: data,
                    beforeSend: add_CSRF,
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: from_django
                })
        }

        function post_json(ajax_data) {
            var url, data, success
            if (typeof(ajax_data) === 'object'){
                if (ajax_data.url !== undefined){
                    url = ajax_data.url
                }
                data = ajax_data.data
                if (ajax_data.success !== undefined){
                    success = ajax_data.success
                }
            } else{
                data = ajax_data
            }

            if (success === undefined){
                success = from_django
            }

            if (url === undefined) {
                url = ajax_helpers.window_location;
            }

            $.ajax(
                {
                    url: url,
                    method: 'post',
                    data: JSON.stringify(data),
                    contentType: 'application/json',
                    beforeSend: add_CSRF,
                    cache: false,
                    success: success
                });
        }

        function from_django(form_response, status, jqXHR) {
            if (contains_file(jqXHR)) {
                download_file(jqXHR, form_response)
            } else if (typeof (form_response) == 'object') {
                process_commands(form_response)
            }
        }

        function get_content(url, store = true) {
            if (store) {
                history.pushState(null, "", url);
                window_location = url
            }
            $.ajax({
                url: url,
                success: from_django
            })
        }

        $(window).on("popstate", function (e) {
            get_content(e.target.window.location.href, false)
        })

        function process_commands(commands) {
            if (ajax_helpers.ajax_busy) {
                window.setTimeout(function () {
                    process_commands(commands)
                }, 100)
            } else {
                while (commands.length > 0) {
                    command = commands.shift()
                    command_functions[command.function](command);
                    if (ajax_helpers.ajax_busy) {
                        window.setTimeout(function () {
                            process_commands(commands)
                        }, 100)
                        break;
                    }
                }
            }
        }

        var tooltip = {
            init: function (selector, url, data) {
                var tooltip_start = false
                $(selector).hover(function () {
                    var _this = this;
                    if (!$(".tooltip:hover").length) {
                        tooltip_start = false
                        $(this).tooltip("dispose");
                    } else {
                        $('.tooltip').mouseleave(function () {
                            tooltip_start = false
                            $(_this).tooltip("dispose");
                        });
                    }
                })
                $(selector).mouseover(function () {
                    if (tooltip_start) {
                        return
                    }
                    tooltip_start = true
                    tooltip_container = $(selector)
                    $.ajax({
                        url: url,
                        data: this.dataset,
                        success: function (data) {
                            tooltip_container.tooltip({
                                placement: "bottom",
                                delay: 0,
                                trigger: 'manual',
                                html: true,
                                title: data,
                            })
                            if (tooltip_start) {
                                tooltip_container.tooltip('show')
                                tooltip_start = false
                            } else {
                                tooltip_container.tooltip('dispose')
                            }
                        },
                        error: function () {
                            tooltip_start = false
                        }
                    })
                })
            }
        }

        var command_functions = {

            html: function () {
                element = $(command.selector)
                if (command.parent == true){
                    element = element.parent()
                }
                element.html(command.html)
            },
            reload: function () {
                ajax_helpers.ajax_busy = true
                location.reload();
            },
            redirect: function () {
                window.location.href = command.url;
            },

            message: function (){
                    alert(command.text);
            }
        };

        return {
            getCookie,
            get_content,
            window_location,
            post_json,
            send_form,
            post_data,
            command_functions,
            process_commands,
            tooltip,
            ajax_busy,
        }
    }()
}
