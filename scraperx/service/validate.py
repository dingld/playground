from typing import List

from w3lib.url import to_native_str
from scraperx.dao.session import SessionLocal
from scraperx.entities.scrape import HtmlScrapeResultEntity
from scraperx.model.rule import HtmlRuleModel
from scraperx.service.parser.cluster import parse_html_cluster
from scraperx.service.parser.sql import parse_html_with_rule
from scraperx.utils.converter import convert_model_to_html_rule_response_entity


def parse_with_rule_id(rule_id: int):
    with SessionLocal() as session:
        model: HtmlRuleModel = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not model:
            return HtmlScrapeResultEntity.construct(status=1, msg="rule id not exists")
    html = to_native_str(model.html)
    rule = convert_model_to_html_rule_response_entity(model)
    url = "https://%s%s" % (rule.domain, rule.path)
    return parse_html_with_rule(url=url, html=html, rule=rule)


def parse_with_cluster(rule_id: int):
    with SessionLocal() as session:
        model: HtmlRuleModel = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not model:
            return HtmlScrapeResultEntity.construct(status=1, msg="rule id not exists")
    html = to_native_str(model.html)
    rule = convert_model_to_html_rule_response_entity(model)
    url = "https://%s%s" % (rule.domain, rule.path)
    return parse_html_cluster(url=url, html=html)


def parse_html_cluster_markers(rule_id: int):
    with SessionLocal() as session:
        model: HtmlRuleModel = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not model:
            return HtmlScrapeResultEntity.construct(status=1, msg="rule id not exists")
    html = to_native_str(model.html)
    rule = convert_model_to_html_rule_response_entity(model)
    url = "https://%s%s" % (rule.domain, rule.path)
    items = parse_html_cluster(url=url, html=html)
    return render_html_markers(html, items)


def render_html_markers(html: str, items: List[HtmlScrapeResultEntity]) -> str:
    javascript = """
        <script>
        function mOver(obj){
            selector = obj.getAttribute('targetCss')
           const myNodeList = document.querySelectorAll(selector);
            for (let i = 0; i < myNodeList.length; i++) {
            newObj = myNodeList[i]
            newObj.style.borderStyle='solid'
            newObj.style.borderColor='red'
            }
        }
        function mOut(obj){
             selector = obj.getAttribute('targetCss')
            const myNodeList = document.querySelectorAll(selector);
            for (let i = 0; i < myNodeList.length; i++) {
            newObj = myNodeList[i]
            newObj.style.borderStyle=null
            newObj.style.borderColor='red'
            }
        }
        </script>
        """

    style = """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted black;
        }
    
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: red;
    
    
            /* 定位 */
            position: absolute;
            z-index: 1;
        }
    
        .tooltip:hover .tooltiptext {
            visibility: visible;
        }
    
                .sidebar {
          position: fixed;
          top: 50%;
          right: 0;
          transform: translateY(-50%);
          width: 200px;
          background-color: #f5f5f5;
          padding: 20px;
        }
    
        .sidebar ul {
          list-style: none;
          margin: 0;
          padding: 0;
        }
    
        .sidebar li {
          margin-bottom: 10px;
        }
    
        .sidebar a {
          text-decoration: none;
          color: #333;
        }
    
        </style>
    
        """

    divs = []
    for i, item in enumerate(items):
        rule = item.rule
        css = rule.name
        div = """
            <div onmouseover="mOver(this)" onmouseout="mOut(this)" class="tooltip mark-toggle" targetCss="%s"> %02d
                <span class="tooltiptext">%s</span>
            </div>
                """ % (css, i + 1, css)
        divs.append(div)
    div = """
        <div class="sidebar">marker
            %s
        </div>
        """ % "\n".join(divs)
    return div + html + javascript
