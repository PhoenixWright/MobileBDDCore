import os

from jinja2 import Environment
from jinja2.loaders import DictLoader

from mobilebdd.reports.base import BaseReporter


Html = u"""
<!DOCTYPE html>
<html>
<head>
    <title></title>
    <style>
        * {
            font-family: "Lucida Console", Monaco, monospace;
            font-size: 11pt;
            -webkit-transition: all 0.2s;
        }

        .feature, .scenario { color: black; }
        .untested { color: gray; }
        .skipped { color: gray; }
        .passed { color: green; }
        .failed { color: red; }

        .accordion { margin-left: 2em; }
        .accordion:hover { cursor: default; }

        h3 {
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0.5em;
            padding-bottom: 0.5em;
            font-weight: normal;
        }
        h3:hover { background-color: rgba(200,200,255,0.3); }
        h3.step {
            padding: 0;
        }
        h3.step .keyword {
            /*font-weight: bold;*/
        }

        div.feature {
            line-height: 1.2;
        }
        div.scenario {
            margin-bottom: 1em;
        }
        div.step {
            padding-left: 2em;
        }
        div.step.message {
            /*max-width: 1024px;*/
        }

        button {
            font-family: sans-serif;
            padding: 0.5em;
        }

        /*
        http://stackoverflow.com/a/248013/3075814
        http://www.longren.org/wrapping-text-inside-pre-tags/
        */
        pre {
            font-family: "Lucida Console", Monaco, monospace;
            white-space: pre-wrap;       /* css-3 */
            white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
            white-space: -pre-wrap;      /* Opera 4-6 */
            white-space: -o-pre-wrap;    /* Opera 7 */
            word-wrap: break-word;       /* Internet Explorer 5.5+ */
        }

        .features {
            width: 65%;
        }

        #screenshot {
            width: 30%;
            height: 100%;
            position: fixed;
            right: 0;
            top: 0;
        }

        .show {
            display: block !important;
        }

        #screenshot img {
            width: auto;
            height: 100%;
            display: none;
        }
    </style>
    <script type="text/javascript"
            src="http://code.jquery.com/jquery-2.1.0.min.js"></script>
</head>
<body>

<button id="only_errors">Only Errors</button>
<button id="expand_all">Expand All</button>
<button id="collapse_all">Collapse All</button>

<div class="features accordion">
    {% for feature in features %}
    <h3 class="feature"><span class="{{feature.status}}">Feature:</span> {{ feature.name }}</h3>

    <div class="feature">
        <div class="scenarios accordion">
            {% for scenario in feature.scenarios %}
            <h3 class="scenario"><span class="{{scenario.status}}">Scenario:</span> {{ scenario.name }}</h3>

            <div class="scenario accordion">
                {% for step in scenario.steps %}
                <h3 class="step {{ step.status }} {{ step.step_type }}" step_id="{{step.id}}"><span class="keyword">{{ step.keyword }}</span> {{ step.name }}</h3>

                {% if step.error_message %}
                <div class="step message {{ step.status }} {{ step.step_type }}">
                    <pre>{{ step.error_message }}</pre>
                </div>
                {% endif %}
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</div>
<div id="screenshot">
    {% for feature in features %}
    {% for scenario in feature.scenarios %}
    {% for step in scenario.steps %}
    {% if step.screenshot_path %}
    <img id="{{step.id}}" src="{{step.screenshot_path}}"/>
    {% endif %}
    {% endfor %}
    {% endfor %}
    {% endfor %}
</div>

</body>
<script type="text/javascript">
$(window).ready(function () {
    var anim_time = 200;

    function only_errors() {
        $('h3').has('.passed').next('div').slideUp(anim_time);
        $('h3').has(':not(.passed)').next('div').slideDown(anim_time);
    }
    function expand_all() {
        $('h3 + div').slideDown(anim_time);
    }
    function collapse_all() {
        $('h3 + div').slideUp(anim_time);
    }

    $('#only_errors').click(only_errors);
    $('#expand_all').click(expand_all);
    $('#collapse_all').click(collapse_all);

    $('.accordion h3').click(function() {
        $(this).find('+ div').toggle(anim_time);
        return false;
    });

    $('h3.step').hover(function() {
        $('#' + $(this).attr('step_id')).addClass('show');
    }, function() {
        $('#' + $(this).attr('step_id')).removeClass('show');
    });

    only_errors();
});
</script>
</html>
"""


class HtmlReporter(BaseReporter):
    """
    outputs a nice html report of the test run
    """

    def __init__(self, config, report_base_dir):
        """
        overload the base init, we dont need the config, so ignore it

        :type config: Configuration
        :param report_base_dir: the base dir where reports will be stored. used
            to find any screenshots to include
        """
        super(HtmlReporter, self).__init__(config)

        self.report_dir = report_base_dir

    def end(self):
        """
        all testing is complete, wrap things up
        """
        jinja_env = Environment(loader=DictLoader({u'html_report': Html}))
        template = jinja_env.get_template(u'html_report')

        # the file paths in the step_screenshot variables are absolute
        # make them relative for the index.html file for portable output
        features = self.features
        for feature in features:
            for scenario in feature.scenarios:
                for step in scenario.steps:
                    if hasattr(step, 'screenshot_path') and step.screenshot_path:
                        # make the report_dir the basis for the relative path
                        step.screenshot_path = os.path.relpath(
                            step.screenshot_path,
                            self.report_dir
                        )

        html = template.render(features=features)

        # make the report dir if it doesnt exist
        try:
            os.makedirs(self.report_dir)
        except OSError:
            if not os.path.isdir(self.report_dir):
                raise

        report_file = os.path.join(
            self.report_dir,
            u'index.html'
        )
        with open(report_file, u'w') as f:
            f.write(html.encode(u'utf8'))
