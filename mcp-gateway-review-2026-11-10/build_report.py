from pathlib import Path
import json, csv, html, re, hashlib, zipfile

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
DATE = '2026-11-10'
SOURCES = []
def source(id, title, publisher, url, kind, supports, published=None):
    SOURCES.append(dict(id=id, title=title, publisher=publisher, url=url, kind=kind,
                        supports=supports, published=published, accessed=DATE))

source('S01','Security Best Practices','MCP project','https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices','Стандарт / руководство','Token passthrough, confused deputy, SSRF, границы доверия')
source('S02','Authorization · revision 2026-07-28','MCP project','https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization','Стандарт','Авторизация HTTP, metadata discovery и audience')
source('S03','Transports · revision 2026-07-28','MCP project','https://modelcontextprotocol.io/specification/2026-07-28/basic/transports','Стандарт','stdio и Streamable HTTP; отделение транспорта от семантики')
source('S04',"Designing MCP Gateway: Uber’s MCP Management Platform",'Uber Engineering','https://www.uber.com/be/en/blog/designing-mcp-gateway/','Внутреннее внедрение','800+ серверов, 5000+ tools; ownership, enablement, tool-level policy, redaction','2026-10-01')
source('S05','Scaling MCP adoption: our reference architecture','Cloudflare','https://blog.cloudflare.com/enterprise-mcp/','Внутреннее внедрение / поставщик','Внутренние remote MCP, Access, portals, DLP и обнаружение обхода','2026-04-14')
source('S06','Closing the agentic AI productionization gap · японская версия','Bloomberg','https://www.bloomberg.co.jp/company/stories/closing-the-agentic-ai-productionization-gap-bloomberg-embraces-mcp/','Внутреннее внедрение','Remote multi-tenant MCP, identity exchange, SSO proxy, registry','2026-01-06')
source('S07','MCP in the Enterprise: Real World Adoption at Block','goose / Angie Jones','https://dev.to/goose_oss/mcp-in-the-enterprise-real-world-adoption-at-block-ci5','Публикация команды внедрения','Кураторский набор собственных MCP, OAuth, keychain и ограничения моделей','2025-04-22')
source('S08','Bloomberg launches Enterprise MCP','Bloomberg via PRNewswire','https://www.prnewswire.com/news-releases/bloomberg-launches-enterprise-mcp-to-seamlessly-connect-bloomberg-data-with-clients-enterprise-ai-applications-302891331.html','Анонс продукта','Entitlements, audit и tool-level limits; это внешний продукт','2026-09-29')
source('S09','AgentCore Gateway overview','AWS','https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html','Документация','Managed gateway, API/Lambda translation, credential injection и semantic selection')
source('S10','Use a Gateway with Policy in AgentCore','AWS','https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/use-gateway-with-policy.html','Документация','Policy охватывает MCP tools; prompts/resources не проходят эту оценку; list и call проверяются отдельно')
source('S11','CreatePolicy API','AWS','https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreatePolicy.html','Документация','Детерминированные Cedar/Dogwood policy, условия по входным параметрам и OAuth claims')
source('S12','MCP server targets','AWS','https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html','Документация','Версии протокола, DEFAULT/DYNAMIC listing; ограничения semantic search и 3LO')
source('S13','Amazon Bedrock AgentCore pricing','AWS','https://aws.amazon.com/bedrock/agentcore/pricing/','Прайс / примеры','Consumption pricing; примеры InvokeTool, Search и отдельной Policy evaluation')
source('S14','About MCP servers in Azure API Management','Microsoft','https://learn.microsoft.com/en-us/azure/api-management/mcp-server-overview','Документация','REST-to-MCP, proxy, auth, Azure Monitor, self-hosted; tools only и scope policies','2026-09-11')
source('S15','MCP server portals are generally available','Cloudflare','https://developers.cloudflare.com/changelog/post/2026-09-24-mcp-portals-ga/','Changelog','GA, service tokens, DLP routing, Logpush, Code Mode policies','2026-09-24')
source('S16','MCP server portals','Cloudflare','https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/','Документация','Portal configuration; DLP request/response; legacy SSE не работает через Gateway routing')
source('S17','AI MCP Servers · ACL tool control','Kong','https://developer.konghq.com/ai-gateway/entities/ai-mcp-server/','Документация','Per-tool ACL, CEL и версии data plane; AI Policies, OTEL')
source('S18','Secure internal MCP gateway','Kong','https://developer.konghq.com/cookbooks/secure-internal-mcp-gateway/','Документация','Корпоративный IdP, conversion-only MCP и per-tool ACL')
source('S19','Introducing Solo Enterprise for agentgateway','Solo.io','https://www.solo.io/blog/introducing-solo-enterprise-for-agentgateway','Анонс продукта','Enterprise lifecycle, fingerprinting, versioning, poisoning/rug-pull protection')
source('S20','Backend authentication','Solo.io','https://docs.solo.io/agentgateway/standalone/latest/documentation/configuration/security/backend-authn/','Документация','Enterprise STS token exchange работает отдельным компонентом')
source('S21','agentgateway repository','agentgateway project','https://github.com/agentgateway/agentgateway','Код / README','Apache-2.0, MCP federation, OAuth, CEL, OTEL, guardrail integrations')
source('S22','MCP Gateway: secure AI agent tool access','Gravitee','https://www.gravitee.io/blog/mcp-gateway','Описание поставщика','Protocol-aware MCP Proxy и общий governance с LLM/A2A')
source('S23','Secure MCP Proxy with OAuth2 · APIM 4.10','Gravitee','https://documentation.gravitee.io/apim/4.10/agent-mesh/secure-mcp-proxy-with-oauth2','Документация','Связка APIM OAuth2 plan и Access Management authorization server')
source('S24','Model Context Protocol middleware','Traefik','https://doc.traefik.io/traefik-hub/mcp-gateway/mcp','Документация','OAuth resource server, JWT и TBAC task/tool/transaction')
source('S25','MCP Gateway best practices','Traefik','https://doc.traefik.io/traefik-hub/mcp-gateway/guides/mcp-gateway-best-practices','Документация','OBO exchange выполняет MCP server; gateway передаёт или удаляет auth context')
source('S26','ContextForge repository','IBM','https://github.com/IBM/mcp-context-forge','Код / README','Apache-2.0, registry/federation, auth/RBAC, plugins, OTEL, Kubernetes')
source('S27','ContextForge SSRF in OAuth gateway registration · CVE-2026-8355','IBM','https://www.ibm.com/support/pages/node/7285723','Бюллетень безопасности','Уязвимы <=1.0.5; исправление 1.0.6; пример риска самого gateway','2026-08-31')
source('S28','MCP Gateway','Docker','https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/','Документация','Контейнерная изоляция, lifecycle, credentials injection, logs/tracing')
source('S29','What is ToolHive?','Stacklok','https://docs.stacklok.com/toolhive','Документация','Apache-2.0 core, Operator, vMCP aggregation, registry, secret management и OTEL')
source('S30','Connector Gateway','Stacklok','https://docs.stacklok.com/connector-gateway','Документация','Enterprise connector-level policy, user identity и credential brokering; отличие от vMCP')
source('S31','MCP Gateway','MintMCP','https://www.mintmcp.com/mcp-gateway','Описание поставщика','Единый endpoint, hosted STDIO, credential management; US/EU, VPC/self-host on request')
source('S32','For Security','MintMCP','https://www.mintmcp.com/for-security','Описание поставщика','Audit, outbound reverse proxy, managed detection policy')
source('S33','Lasso MCP Gateway repository','Lasso Security','https://github.com/lasso-security/mcp-gateway','Код / README','MIT, plugin-based gateway, scanner; advanced guardrails вызывают Lasso API')
source('S34','MCP Identity Gateway concepts','Aembit','https://docs.aembit.io/user-guide/deploy-install/mcp-identity-gateway/concepts-mcp-gateway/','Документация','Две identity и два policy leg, managed/self-host Linux, content providers')
source('S35','IAM for Agentic AI pricing','Aembit','https://aembit.io/pricing/','Прайс','3 agents free; Teams $20/agent/month с началом от 10; retention; Enterprise custom')
source('S36','MCP Gateway features','Portkey / Palo Alto Networks','https://portkey.ai/features/mcp','Описание поставщика','Текущее имя Prisma AIRS AI Gateway; MCP auth/RBAC, runtime policy, SaaS/private deployment')
source('S37','Palo Alto Networks completes acquisition of Portkey','Palo Alto Networks','https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-portkey-to-secure-ai-agents','Пресс-релиз','Приобретение завершено 29 мая 2026','2026-05-29')
source('S38','MCP Gateway overview','Maxim AI / Bifrost','https://docs.getbifrost.ai/mcp/overview','Документация','MCP client/server, virtual MCPs, execution, Code Mode, resources/prompts')
source('S39','MCP authentication with Bifrost','Maxim AI','https://www.getmaxim.ai/topics/mcp-gateway/mcp-authentication','Техническая статья поставщика','Inbound OAuth/keys, per-user outbound auth; token_exchange Enterprise')
source('S40','Bifrost repository','Maxim AI','https://github.com/maximhq/bifrost','Код / README','Apache-2.0, AI gateway; private enterprise deployments')
source('S41','Introducing the TrueFoundry MCP Gateway','TrueFoundry','https://www.truefoundry.com/blog/introducing-truefoundry-mcp-gateway','Техническая статья поставщика','Registry, groups, PAT/VAT, per-user OAuth, virtual MCP servers')
source('S42','MCP server hosting','TrueFoundry','https://www.truefoundry.com/blog/mcp-server-hosting','Техническая статья поставщика','Kubernetes, VPC/on-prem/air-gap; OTEL; tool-level control')
source('S43','Enterprise MCP governance','TrueFoundry','https://www.truefoundry.com/blog/enterprise-mcp-governance-control-audit-secure-mcp-server-access','Техническая статья поставщика','Inbound identity vs outbound 3LO; lifecycle credentials и IdP integration')
source('S44','Microsoft MCP Gateway repository','Microsoft','https://github.com/microsoft/mcp-gateway','Код / README','Отдельный от Azure APIM проект; требует revision 2026-07-28 без protocol downgrade')
source('S45','Gateway egress · MCP Security Testing Guide','OWASP project','https://github.com/OWASP/MCP-Security-Testing-Guide/blob/main/03.%20MCP%20Threats%20and%20Attack%20Patterns/3.16-gateway-egress.md','Руководство проекта','Trust zones и gateway enforcement по identity/client/server/tool/action/data; evolving guide')

PRODUCTS = []
def product(id, name, group, deploy, license, summary, strengths, caveat, fit, price, matrix, refs):
    PRODUCTS.append(dict(id=id,name=name,group=group,deployment=deploy,license=license,summary=summary,
                         strengths=strengths,caveat=caveat,fit=fit,pricing=price,features=matrix,sources=refs,verified_at=DATE))
# Feature values are evidence labels, not results of hands-on tests.
product('aws','Amazon Bedrock AgentCore Gateway','Облачные платформы',['managed'],'Коммерческий managed service',
        'Облачная точка подключения MCP, API и Lambda с управлением входной и исходящей аутентификацией.',
        'Credential injection, semantic tool selection; Policy in AgentCore задаёт условия по claims и параметрам вызова.',
        'Policy проверяет только tools: prompts и resources требуют отдельного контроля. DYNAMIC listing несовместим с semantic search и outbound 3LO.',
        'AWS-first агенты и интеграция существующих сервисов.',
        'Оплата операций Gateway; Policy и поиск считаются отдельно. Инфраструктура, логи и backend добавляют расходы.',
        ['doc','doc','doc','integration','verify'],['S09','S10','S11','S12','S13'])
product('azure','Azure API Management','Облачные платформы',['managed','self'],'Коммерческие tiers APIM',
        'Публикует REST APIs как MCP tools и проксирует существующие удалённые MCP-серверы.',
        'JWT/Entra ID, quotas, IP policies, Azure Monitor; discovery через отдельный Azure API Center.',
        'В текущем overview: только tools; prompts/resources и APIM workspaces не поддержаны. Policies по умолчанию охватывают все tools сервера: per-tool гранулярность нужно проектировать и проверять.',
        'Организации с действующим Azure API Management и Entra ID.',
        'Стоимость tier/capacity APIM и сопутствующих Azure-сервисов; точный региональный расчёт нужен отдельно.',
        ['doc','limited','verify','integration','verify'],['S14'])
product('cloudflare','Cloudflare MCP server portals','Облачные платформы',['managed'],'Коммерческий Cloudflare One / Access stack',
        'Единый endpoint к одобренным remote MCP-серверам с политиками доступа и аудитом.',
        'Portals GA с 24.09.2026; service tokens для M2M, Logpush; Gateway routing добавляет DLP запросов и ответов.',
        'DLP требует соответствующей настройки и entitlement Cloudflare. Legacy SSE не поддерживается через Gateway routing. Runtime произвольного MCP-кода — отдельная задача.',
        'Корпоративные IDE и AI-клиенты в среде Cloudflare Zero Trust.',
        'Проверить стоимость Access, Gateway, DLP, логов и Workers, если серверы также размещаются у Cloudflare.',
        ['doc','doc','verify','integration','verify'],['S15','S16'])
product('kong','Kong AI Gateway','API management',['managed','self'],'Enterprise AI capabilities / коммерческие планы',
        'MCP-governance внутри API/AI-платформы: публикация tools и proxy существующих серверов.',
        'Server/per-tool ACL, consumer identity, AI Policies и OTEL. CEL ACL требует data plane 3.16+.',
        'У per-tool ACL своя семантика override: исключение заменяет базовые списки. Проверить версию, режим MCP Server и лицензирование нужных plugins.',
        'Компании с Kong/Konnect и командой API platform.',
        'Коммерческая конфигурация и capacity; цену обычного API gateway нельзя считать ценой MCP Enterprise.',
        ['doc','doc','verify','integration','verify'],['S17','S18'])
product('gravitee','Gravitee MCP Proxy','API management',['managed','self'],'Коммерческие возможности APIM/Agent Management',
        'Protocol-aware MCP proxy рядом с управлением API, LLM и A2A.',
        'OAuth2 plan в APIM + Access Management; политики на уровне MCP methods и tools заявлены в описании продукта.',
        'Подтвердить tool/argument enforcement именно в выбранной версии и плане; OAuth-сценарий может требовать отдельный компонент AM.',
        'Единая программа API, event и agent governance.',
        'Запросить коммерческую конфигурацию APIM, AM и agent/AI capabilities.',
        ['doc','doc','verify','integration','verify'],['S22','S23'])
product('traefik','Traefik Hub MCP Gateway','API management',['self'],'Коммерческий Traefik Hub',
        'MCP middleware с OAuth resource metadata и Task-Based Access Control.',
        'TBAC ограничивает task, tool и transaction; правила используют JWT claims и параметры запроса.',
        'OBO token exchange реализует MCP-сервер, а gateway передаёт либо удаляет auth context. Это нужно включить в проект интеграции.',
        'Kubernetes/Traefik platform с требованиями к параметрам транзакций.',
        'Лицензия Hub и эксплуатация собственной инфраструктуры; предложение поставщика.',
        ['doc','doc','doc','integration','verify'],['S24','S25'])
product('solo','agentgateway / Solo Enterprise','Открытая платформа',['self'],'Apache-2.0 OSS + коммерческий Solo Enterprise',
        'MCP/LLM/A2A proxy с федерацией tools, OAuth, CEL policy и телеметрией.',
        'OSS покрывает базовые proxy/security controls. Enterprise добавляет lifecycle/fingerprinting и STS для backend token exchange.',
        'Разделять OSS и Enterprise в RFP. STS — отдельный сервис; coverage lifecycle-защит и отказоустойчивость проверять на конкретном релизе.',
        'Собственная platform engineering команда и смешанная AI-инфраструктура.',
        'OSS без лицензионного платежа; compute, эксплуатация и Enterprise support оплачиваются отдельно.',
        ['doc','doc','verify','integration','verify'],['S19','S20','S21'])
product('ibm','IBM ContextForge','Открытая платформа',['self'],'Apache-2.0',
        'Открытые registry, proxy и federation для MCP, A2A и REST/gRPC.',
        'Централизованный каталог, RBAC, plugins, OpenTelemetry и Kubernetes deployment.',
        'Команда отвечает за hardening, state stores и обновления. IBM публиковала CVE-2026-8355: OAuth registration SSRF до 1.0.5 включительно; фикс 1.0.6. Это не оценка текущего релиза.',
        'Self-hosted платформа с кастомными политиками и интеграциями.',
        'Лицензия OSS; инфраструктура, разработка политик, мониторинг и сопровождение.',
        ['doc','doc','verify','integration','verify'],['S26','S27'])
product('stacklok','ToolHive / Stacklok Enterprise','Открытая платформа',['self','local'],'Apache-2.0 core + коммерческий Enterprise',
        'Runtime, registry и gateway vMCP; Kubernetes Operator управляет парком MCP-серверов.',
        'Контейнеризация, secrets, network filtering и OTEL. Enterprise Connector Gateway связывает identity, connector policy и backend credentials.',
        'vMCP и Enterprise Connector Gateway — разные компоненты. Состав console, IdP integrations и support закрепить в выбранной редакции.',
        'Организации, которым нужны и gateway, и управление исполнением MCP-кода.',
        'OSS + эксплуатация; Enterprise платформа и enterprise connectors по подписке / предложению.',
        ['doc','doc','verify','integration','doc'],['S29','S30'])
product('docker','Docker MCP Gateway','Локальная среда',['local'],'Docker ecosystem; условия Desktop и компонентов отдельно',
        'Управляет локальными MCP-серверами в Docker-контейнерах и подключает к ним AI-клиентов.',
        'Lifecycle, credential injection, ограничения privileges/network/resources, logging и call tracing.',
        'Документированный локальный сценарий не подтверждает готовый корпоративный multi-tenant control plane. Изоляция контейнеров зависит от настройки хоста.',
        'Контролируемая разработческая среда и локальные stdio tools.',
        'Учитывать подписку Docker Desktop организации и стоимость endpoint management.',
        ['limited','verify','verify','verify','doc'],['S28'])
product('portkey','Prisma AIRS AI Gateway / Portkey','Единая AI-платформа',['managed','self'],'Коммерческая платформа; состав OSS отдельно',
        'Общий контур governance для моделей и MCP; Portkey входит в Palo Alto Networks с 29.05.2026.',
        'MCP registry, OAuth/JWT, server/tool RBAC, audit/traces и runtime policies заявлены на текущей странице продукта.',
        'Актуальные naming, SKU, private deployment и границы OSS закрепить в договоре: старые обзоры Portkey описывают более раннее состояние продукта.',
        'Единая платформа AI governance и интеграция с security stack Palo Alto.',
        'Актуальное предложение Prisma AIRS; старые публичные тарифы Portkey не использованы.',
        ['doc','doc','verify','doc','verify'],['S36','S37'])
product('bifrost','Bifrost · Maxim AI','Единая AI-платформа',['self'],'Apache-2.0 core + Enterprise',
        'Один deployment для LLM и MCP с virtual MCPs, фильтрацией tools и Code Mode.',
        'Inbound OAuth/keys, upstream per-user OAuth; token exchange в Enterprise. Есть общий контур identity и наблюдаемости.',
        'Заявления о микросекундах overhead не сопоставимы с полным security path. Code Mode требует проверки sandbox и авторизации каждого вложенного tool call.',
        'Самостоятельно размещаемый gateway для моделей и tools.',
        'OSS + инфраструктура; Enterprise governance и support по предложению.',
        ['doc','doc','verify','integration','verify'],['S38','S39','S40'])
product('mint','MintMCP','Специализированный MCP',['managed','self'],'Коммерческий managed / private product',
        'Готовый каталог и endpoint для корпоративных AI-клиентов с хранением credentials и аудитом.',
        'Hosting собственных, в том числе STDIO, серверов; единая policy при смене AI-клиента. Указаны managed US/EU.',
        'VPC/self-hosted доступны по запросу. Проверить гранулярность параметров, isolation, вывоз логов и условия private deployment.',
        'Быстрое внедрение MCP для сотрудников без собственной gateway-команды.',
        'Коммерческое предложение; отдельно запросить hosting, users, retention и private networking.',
        ['doc','doc','verify','integration','doc'],['S31','S32'])
product('lasso','Lasso MCP Gateway','Специализированный MCP',['local','self'],'MIT gateway + коммерческие API/guardrails',
        'Расширяемый gateway с plugins для inspection запросов/ответов и сканированием MCP перед загрузкой.',
        'Scanner проверяет репутацию и tool descriptions; Lasso plugin добавляет проверки prompt injection и утечки данных.',
        'Advanced guardrails обращаются к Lasso API: проверить передачу payload и режим отказа. README не доказывает полноту enterprise IAM/HA.',
        'Security inspection существующих MCP workflows и расширение собственными plugins.',
        'MIT core; коммерческие Lasso services, инфраструктура и сопровождение.',
        ['verify','verify','verify','integration','verify'],['S33'])
product('aembit','Aembit MCP Identity Gateway','Специализированный MCP',['managed','self'],'Коммерческий IAM / gateway',
        'Identity-aware proxy с учётом человека и AI-клиента и изоляцией downstream credentials.',
        'Client-to-gateway и gateway-to-server policies; managed или self-host Linux. Content Security подключается провайдером.',
        'Идентификатор зарегистрированного клиента / redirect URI не равен аппаратной аттестации процесса. Проверить детализацию tool/argument policy и threat model клиента.',
        'Крупные организации, где основная проблема — delegation и non-human identity.',
        'Starter: 3 agents; Teams: $20/agent/мес., от 10 agents; Enterprise custom. Важно определить единицу agent и retention.',
        ['doc','doc','verify','integration','verify'],['S34','S35'])
product('truefoundry','TrueFoundry MCP Gateway','Единая AI-платформа',['self'],'Коммерческая AI-платформа',
        'MCP registry и virtual servers вместе с LLM/agent gateway в собственной инфраструктуре.',
        'PAT/VAT либо IdP token на входе, per-user OAuth на выходе, server groups, curated toolsets и OTEL.',
        'Проверить изоляцию virtual accounts, override custom headers, доступность granular policy в нужной редакции и outbound data paths.',
        'Собственная Kubernetes/LLMOps среда, VPC/on-prem/air-gap требования.',
        'Коммерческая конфигурация; platform, compute и эксплуатация учитываются отдельно.',
        ['doc','doc','verify','integration','verify'],['S41','S42','S43'])

CASE_STUDIES = [
 dict(company='Uber',date='01 октября 2026',label='Внутренний gateway · production по сообщению компании',metric='800+ / 5 000+',metric_label='MCP-серверов / tools',
      text='Собственный gateway объединяет registry/control plane и runtime/data plane. Он публикует существующие HTTP, gRPC и TChannel сервисы как tools и подключает native MCP. Команды сервисов сохраняют ownership: новые tools выключены до review, изменения описаний требуют согласования и допускают rollback.',
      security='Авторизация по humans/services/agents, tool-level overrides и redaction чувствительных ответов. Для внешних сервисов отдельный компонент обменивает внутреннюю identity на third-party credential.',
      takeaway='Заимствовать модель ownership и controlled enablement; число подключённых tools само по себе не показывает уровень безопасности.',refs=['S04']),
 dict(company='Cloudflare',date='14 апреля 2026',label='Внутренняя практика · поставщик применяет свой стек',metric='SSO + DLP',metric_label='контроль доступа и потоков данных',
      text='Компания описывает централизованное размещение remote MCP для внутренних источников. Сотрудники подключаются через Access и MCP server portals; администраторы управляют набором доступных tools и DLP.',
      security='Отдельный сетевой контроль обнаруживает remote MCP, к которым обращаются в обход portal: по доменам, путям и JSON-RPC признакам. Это расширяет покрытие за пределы одного endpoint.',
      takeaway='Маршрутизация через gateway становится границей защиты только при контроле обходных путей. Self-report поставщика не является независимым тестом.',refs=['S05']),
 dict(company='Bloomberg',date='06 января 2026 · японская публикация',label='Внутренняя архитектура · identity middleware',metric='User + workload',metric_label='две identity в цепочке доступа',
      text='Bloomberg описывает remote multi-tenant MCP-инфраструктуру с middleware для identity, access control и observability. Клиентский proxy выполняет SSO/authentication; identity exchange формирует канонические identity пользователя и workload.',
      security='Компания также описывает развитие внутреннего registry с metadata и usage policies. Это показывает переход от интеграции отдельных tools к общему governance.',
      takeaway='Делегация identity — самостоятельная инфраструктурная задача. Внешний Bloomberg Enterprise MCP, анонсированный в сентябре, — отдельный продукт с entitlements и audit.',refs=['S06','S08']),
 dict(company='Block',date='22 апреля 2025',label='Историческая практика MCP · наличие gateway не подтверждено',metric='Curated tools',metric_label='одобренные собственные интеграции',
      text='Команда goose сообщает о повседневном использовании MCP тысячами сотрудников. В описанной конфигурации внутренние MCP написаны инженерами Block, одобренный набор предустановлен, OAuth встроен в локальные серверы, tokens хранятся в keychain.',
      security='Корпоративные model endpoints, ограничения на категории данных и в отдельных серверах — LLM allowlists и ограничения передачи результатов между системами.',
      takeaway='Полезный пример governance до централизации. Публикация не доказывает внедрение MCP gateway или текущее состояние Block в ноябре 2026.',refs=['S07'])
]

REQUIREMENTS = [
 ('P0','Identity и delegation','Связать пользователя, workload, tenant и environment. Раздельно проверять входной token и полномочия к backend; поддержать short-lived credentials и отзыв.','Неверный audience/issuer отклонён; user A не получает credential или данные user B.','IAM + Platform',['S01','S02','S34']),
 ('P0','Авторизация при каждом действии','Фильтровать discovery и повторно проверять invocation. Условия должны учитывать tool, аргументы, целевой объект, среду и класс действия.','Прямой tools/call к скрытому tool запрещён; запрет prod нельзя обойти заменой аргумента.','Security + владелец API',['S10','S11','S24']),
 ('P0','Управляемые credentials','Изолировать секреты backend от модели и клиента; хранить отдельно по user/tenant, обеспечивать rotation и минимальные scopes.','В configs, traces и ошибках нет ключей; увольнение пользователя прекращает доступ в согласованный срок.','IAM + SRE',['S09','S30','S43']),
 ('P0','Принудительный маршрут','Контролировать прямые MCP-подключения, доступ к backend, egress и установку локальных stdio серверов.','Отдельный клиент и ноутбук не обходят политику прямым HTTP или запуском локального MCP.','Endpoint + Network',['S05','S45']),
 ('P0','Supply chain и изменения tools','Владелец и проверенная версия каждого сервера; pinned artifacts, schema/description diff, approval и rollback. Аннотации readOnly — подсказки, а не права.','Изменённое описание или образ попадает на review; незнакомый tool не включается автоматически.','AppSec + владелец сервиса',['S04','S19','S29']),
 ('P0','Audit без утечки данных','Логировать identity, tool, решение, policy version, target, результат и trace ID. Payload хранить избирательно, с redaction, сроками и разграничением доступа.','SOC восстанавливает цепочку решения; audit не раскрывает tokens, PII и соседний tenant.','SOC + Data governance',['S15','S17','S26']),
 ('P0','Безопасность самого gateway','Разделить admin/control и data plane, ограничить регистрацию upstream URL, защитить metadata fetch, secrets и egress.','SSRF в registration/OAuth discovery не достигает metadata и внутренних сервисов вне allowlist.','AppSec + SRE',['S01','S27']),
 ('P1','Inspection контента и DLP','Проверять аргументы, tool output и tool descriptions; разделять блокировку, маскирование и alert. Задать поведение при недоступности scanner.','Canary secret не покидает границу; injection corpus измеряет и пропуски, и ложные блокировки.','AI Security + Data',['S16','S33']),
 ('P1','Подтверждение опасных операций','Согласование должно быть связано с точными tool/target/arguments, ограничено сроком и защищено от replay; step-up для high-impact actions.','Смена суммы или адресата после approval требует нового решения; повторное исполнение заблокировано.','Владелец процесса',['S45']),
 ('P1','Runtime isolation','Для размещаемого MCP-кода — ограниченные filesystem/network, container sandbox, quotas и отсутствие host secrets. Remote proxy сам по себе не изолирует сервер.','Скомпрометированный tool не читает секреты хоста и не обращается к произвольным адресам.','Platform + Runtime security',['S28','S29']),
 ('P1','Надёжность и управляемый масштаб','Quotas per caller/tool, timeouts, backpressure, HA, tenant-aware caching; осмысленные retries только для безопасных операций.','Отказ upstream не останавливает других tenants; timeout не вызывает повторную запись.','SRE',['S14','S26']),
 ('P1','Протокол и удобство внедрения','Фиксировать MCP revision, transports, tools/resources/prompts, OAuth-клиенты и extension support. Каталог должен облегчать approved path.','Матрица реальных IDE/agents проходит reconnect, revoke, pagination и несовпадение revisions.','Developer platform',['S03','S12','S44'])
]

THREATS = [
 ('Prompt injection в результате tool','Инспекция ответов, маркировка недоверенных данных, least privilege и limits на последующие действия.','Фильтр не даёт гарантии распознавания намерения; бизнес-авторизацию следует проверять независимо от текста.'),
 ('Tool poisoning / rug pull','Review и pinning metadata/schema, fingerprinting и повторное одобрение изменений.','Подпись подтверждает происхождение; она не доказывает, что логика tool безопасна.'),
 ('Confused deputy / кража token','Audience-bound tokens, отдельные credentials на каждый hop, consent и scoped token exchange.','Проброс общего superuser credential сохраняет чрезмерные права за gateway.'),
 ('Cross-tenant утечка','Identity-bound credential stores, cache keys с tenant/user context и backend object-level authorization.','Tool-level allow не заменяет проверку владельца конкретной записи или документа.'),
 ('Exfiltration через разрешённые tools','DLP, минимизация ответов, allowlist направлений и корреляция read → external write.','Допустимые по отдельности чтение и отправка могут образовать нежелательную цепочку.'),
 ('Обход gateway','Managed client configuration, endpoint policy, egress и закрытые backend endpoints.','Прямой SDK/API/CLI или локальный stdio процесс может идти другим маршрутом.'),
 ('SSRF / компрометация control plane','URL/redirect validation, network egress, admin RBAC, patching, hardened secrets store.','Сам gateway концентрирует credentials и становится критичным активом.'),
 ('Повторные действия и cost abuse','Rate/transaction limits, idempotency, бюджеты, ограничение loops и per-tenant quotas.','Автоматический retry после неизвестного результата способен создать дублирующую запись.')
]

POC = [
 ('G01','Identity isolation','Подменить issuer/audience, смешать user/tenant и повторить запрос после отзыва доступа.','Ни один неверный token не исполняет backend call; измерено время отзыва.'),
 ('G02','Discovery ≠ authorization','Убрать tool из tools/list и вызвать его напрямую по известному имени.','Deny на invocation, без выполнения backend.'),
 ('G03','Arguments / object permissions','Разрешить read в dev, затем заменить env, tenant, object ID и объём выдачи.','Проверка каждого параметра и backend ACL, включая границу tenant.'),
 ('G04','Все MCP primitives','Проверить tools/call, resources/read, prompts/get и применяемые extensions.','Нет необъявленных путей доступа; неподдержанные capabilities отключены.'),
 ('G05','Credentials и egress','Проверить traces/errors, auth overrides, OAuth metadata, redirect и upstream URL registration.','Нет секретов в логах; SSRF не достигает запрещённых адресов.'),
 ('G06','Изменения и poisoning','Обновить description/schema/образ после initial approval; добавить malicious metadata.','Работают diff/review/rollback; stale catalog не открывает новый tool.'),
 ('G07','DLP и injection','Canary PII/secrets в arguments и responses, а также вредоносные инструкции в metadata/output.','Считать пропуски и false positives; authorization остаётся действенной при пропуске scanner.'),
 ('G08','Approval integrity','После одобрения сменить target/amount, затем повторить согласованный вызов.','Повторное согласование при изменении; replay отклоняется.'),
 ('G09','Bypass и runtime','Прямое подключение к MCP/backend; локальный stdio; попытка чтения host file/секрета.','Подтверждено фактическое покрытие endpoint/network/runtime controls.'),
 ('G10','Отказы и повторная запись','Отключить IdP/policy/scanner/upstream; оборвать ответ после записи.','Заранее определён fail-closed для привилегированных действий; нет double write.'),
 ('G11','Audit и privacy','Собрать цепочку user → agent → gateway → backend по одному trace.','Есть policy version/decision и раздельные identities; tokens и лишний payload отсутствуют.'),
 ('G12','Нагрузка и совместимость','Реальные клиенты, revisions, pagination, reconnect; замер с policy и inspection.','Согласованный SLO по p95/p99, error rate, throughput и стоимости; результаты воспроизводимы.')
]

def dump(name, obj):
    (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dump('sources.json',SOURCES)
dump('solutions.json',PRODUCTS)
dump('enterprise-cases.json',CASE_STUDIES)
dump('requirements.json',[dict(priority=x[0],name=x[1],requirement=x[2],acceptance=x[3],owner=x[4],sources=x[5]) for x in REQUIREMENTS])
dump('poc-checklist.json',[dict(id=x[0],control=x[1],test=x[2],acceptance=x[3]) for x in POC])
dump('research-log.json',dict(
    accessed=DATE,
    method='Web search, чтение официальной документации, engineering-публикаций и репозиториев. Notes — собственные краткие пересказы, не копии страниц.',
    tests_performed_on_products=False,
    source_notes=[dict(source_id=s['id'],url=s['url'],kind=s['kind'],notes=s['supports']) for s in SOURCES],
    selection_decisions=[
        'Независимые рекламные рейтинги и Reddit не использованы как доказательства возможностей и внедрений.',
        'Uber и Cloudflare: прямые публикации о внутреннем gateway / portal.',
        'Bloomberg: внутреннее identity middleware отделено от внешнего Enterprise MCP продукта.',
        'Block: исторический контекст governance; gateway adoption не подтверждён.',
        'Английский Bloomberg URL вернул HTTP 403; использована официальная японская версия.',
        'Azure APIM отделён от microsoft/mcp-gateway.',
        'Portkey актуализирован с учётом закрытой сделки Palo Alto Networks от 29.05.2026.',
        'Не назначены численные рейтинги продуктов; статусы относятся к публичному описанию, а не efficacy.',
        'Argument-level policy Kong и agentgateway требует подтверждения для выбранного режима/редакции: общего упоминания CEL недостаточно.',
        'Полные страницы и дословные длинные выдержки не сохранялись в пользовательский комплект.'
    ]))
with (DATA/'comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['Решение','Категория','Размещение','Лицензия','Identity','Tool policy','Argument policy','Content inspection','Runtime isolation','Ограничения / проверить','Источники','Дата'])
    for p in PRODUCTS: w.writerow([p['name'],p['group'],', '.join(p['deployment']),p['license'],*p['features'],p['caveat'],','.join(p['sources']),DATE])
with (DATA/'poc-checklist.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','Контроль','Проверка','Критерий приёмки','Результат','Ссылка на evidence']);w.writerows([list(x)+['',''] for x in POC])

E=html.escape
SOURCE_MAP={s['id']:s for s in SOURCES}
def refs(ids):
    return '<span class="refs">'+''.join(f'<a href="#{s}" title="{E(SOURCE_MAP[s]["title"])}">{s}</a>' for s in ids)+'</span>'
def chapter(n, label, title, intro):
    return f'<div class="chapter"><span>{n} / {label}</span><h2>{title}</h2><p>{intro}</p></div>'
def status(s):
    labels={'doc':'Описано','integration':'Интеграция','verify':'Проверить','limited':'Ограничено'}
    return f'<span class="status {s}"><i></i>{labels[s]}</span>'

TEMPLATE = (ROOT/'template.html').read_text(encoding='utf-8')
cases=''.join(f'''<article class="case"><div class="case-top"><h3>{c['company']}</h3><span>{c['date']}</span></div><div class="eyebrow">{c['label']}</div><div class="case-metric">{c['metric']}</div><small>{c['metric_label']}</small><p>{c['text']}</p><p>{c['security']}</p><div class="takeaway"><b>Вывод для архитектуры.</b> {c['takeaway']}</div>{refs(c['refs'])}</article>''' for c in CASE_STUDIES)
requirements=''.join(f'<tr><td><span class="priority {r[0]}">{r[0]}</span><strong>{r[1]}</strong><small>{r[4]}</small></td><td>{r[2]}{refs(r[5])}</td><td>{r[3]}</td></tr>' for r in REQUIREMENTS)
threats=''.join(f'<tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td></tr>' for r in THREATS)
matrix=''.join(f'<tr data-product="{p["id"]}"><td><a href="#product-{p["id"]}">{p["name"]}</a><small>{p["group"]}</small></td>'+''.join(f'<td>{status(x)}</td>' for x in p['features'])+f'<td>{refs(p["sources"])}</td></tr>' for p in PRODUCTS)
DEP={'managed':'Managed','self':'Self-host / private','local':'Local runtime'}
cards=''.join(f'''<article class="product" id="product-{p['id']}" data-group="{E(p['group'])}" data-deploy="{' '.join(p['deployment'])}" data-search="{E((p['name']+' '+p['group']+' '+p['fit']).lower())}"><div class="product-label">{p['group']}</div><h3>{p['name']}</h3><div class="tags">{''.join(f'<span>{DEP[d]}</span>' for d in p['deployment'])}</div><p class="product-summary">{p['summary']}</p><p><b>Возможности.</b> {p['strengths']}</p><p class="product-caveat"><b>Условия и проверка.</b> {p['caveat']}</p><dl><dt>Подходит</dt><dd>{p['fit']}</dd><dt>Лицензия</dt><dd>{p['license']}</dd><dt>Экономика</dt><dd>{p['pricing']}</dd></dl><div class="product-foot">Документы и заявления поставщика {refs(p['sources'])}</div></article>''' for p in PRODUCTS)
poc=''.join(f'<tr><td><code>{x[0]}</code><strong>{x[1]}</strong></td><td>{x[2]}</td><td>{x[3]}</td></tr>' for x in POC)
sources=''.join(f'<li id="{s["id"]}"><span class="source-id">{s["id"]}</span><div><a href="{E(s["url"])}" target="_blank" rel="noopener noreferrer">{E(s["title"])}</a><p>{E(s["publisher"])} · {s["kind"]}'+(f' · {s["published"]}' if s['published'] else '')+f'</p><small>{E(s["supports"])}</small></div></li>' for s in SOURCES)
replacements={'{{CASES}}':cases,'{{REQUIREMENTS}}':requirements,'{{THREATS}}':threats,'{{MATRIX}}':matrix,'{{PRODUCTS}}':cards,'{{POC}}':poc,'{{SOURCES}}':sources,'{{CATALOG}}':json.dumps(PRODUCTS,ensure_ascii=False).replace('</','<\\/')}
for key,value in replacements.items(): TEMPLATE=TEMPLATE.replace(key,value)
(ROOT/'report.html').write_text(TEMPLATE,encoding='utf-8')
print(f'Created report: {len(TEMPLATE.encode())} bytes, {len(PRODUCTS)} products, {len(SOURCES)} sources')
