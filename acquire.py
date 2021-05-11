import requests
import bs4
import pandas as pd
import re
from requests import get
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union, cast
import os
import json
from env import github_token, github_username
headers = {"Authorization": f"token {github_token}", "User-Agent": github_username}

'''
Takes a url from blog posts on the codeup website and returns the title, date, and content
posted on that blog
'''

def acquire_codeup_blog(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = bs4.BeautifulSoup(html)
    title = soup.find('title').text
    content = soup.find(class_ = 'jupiterx-post-content').text
    date = soup.find(itemprop="datePublished").text
    return {
        "title": title,
        "date": date,
        "content": content}

'''
Has multiple urls for blog posts on the codeup website and extracts the title, date, and content from all of them
'''

def acquire_all_blogs():
    blog_list = ['https://codeup.com/codeups-data-science-career-accelerator-is-here/',
                'https://codeup.com/data-science-myths/',
                'https://codeup.com/data-science-vs-data-analytics-whats-the-difference/',
                'https://codeup.com/10-tips-to-crush-it-at-the-sa-tech-job-fair/',
                'https://codeup.com/competitor-bootcamps-are-closing-is-the-model-in-danger/']
    return pd.DataFrame([acquire_codeup_blog(blog) for blog in blog_list])

'''
Takes in a soup created from an article url and extracts the title, content, and category from that article
'''

def get_article(soup, category):
    title = soup.find(itemprop="headline").text
    content = soup.find(itemprop="articleBody").text
    return {
        "title": title,
        "content": content,
        "category": category}

'''
Takes in a specified category and extracts the title, content, and category from each article falling under that category
'''

def get_articles(category):
    base = "https://inshorts.com/en/read/"
    url = base + category
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text)
    articles = soup.select(".news-card")
    output = []
    for article in articles:
        article_data = get_article(article, category) 
        output.append(article_data)
    return output

'''
Takes in a list of categories and extracts the title, content, and category from each article falling under a category in the the category list
'''

def get_all_inshorts(category_list):

    all_inshorts = []

    for category in category_list:
        all_category_articles = get_articles(category)
        all_inshorts = all_inshorts + all_category_articles
    
    df = pd.DataFrame(all_inshorts)
    return df

def github_api_request(url: str) -> Union[List, Dict]:
    response = requests.get(url, headers=headers)
    response_data = response.json()
    if response.status_code != 200:
        raise Exception(
            f"Error response from github api! status code: {response.status_code}, "
            f"response: {json.dumps(response_data)}"
        )
    return response_data

def get_repo_language(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}"
    repo_info = github_api_request(url)
    if type(repo_info) is dict:
        repo_info = cast(Dict, repo_info)
        if "language" not in repo_info:
            raise Exception(
                "'language' key not round in response\n{}".format(json.dumps(repo_info))
            )
        return repo_info["language"]
    raise Exception(
        f"Expecting a dictionary response from {url}, instead got {json.dumps(repo_info)}"
    )

def get_repo_contents(repo: str) -> List[Dict[str, str]]:
    url = f"https://api.github.com/repos/{repo}/contents/"
    contents = github_api_request(url)
    if type(contents) is list:
        contents = cast(List, contents)
        return contents
    raise Exception(
        f"Expecting a list response from {url}, instead got {json.dumps(contents)}"
    )

def get_readme_download_url(files: List[Dict[str, str]]) -> str:
    """
    Takes in a response from the github api that lists the files in a repo and
    returns the url that can be used to download the repo's README file.
    """
    for file in files:
        if file["name"].lower().startswith("readme"):
            return file["download_url"]
    return ""

def process_repo(repo: str) -> Dict[str, str]:
    """
    Takes a repo name like "gocodeup/codeup-setup-script" and returns a
    dictionary with the language of the repo and the readme contents.
    """
    contents = get_repo_contents(repo)
    readme_download_url = get_readme_download_url(contents)
    if readme_download_url == "":
        readme_contents = ""
    else:
        readme_contents = requests.get(readme_download_url).text
    return {
        "repo": repo,
        "language": get_repo_language(repo),
        "readme_contents": readme_contents,
    }

def get_the_repos(url):
    response = requests.get(url)
    html = response.text
    soup = bs4.BeautifulSoup(html)
    bleh = soup.find(class_="Link--muted")['href']
    bleh = soup.find_all(class_="Link--muted")
    hold = []
    for item in bleh:
        hold.append(item['href'])
    regexp = r'\/.*\/.*?'
    lister = []
    for item in hold:
        lister.append(re.findall(regexp, item))
    for i in range(0, len(lister)):
        lister[i] = str(lister[i])
        lister[i] = lister[i][3:-3]
    return lister

def get_all_repos(orig_url):
    split_url = orig_url.split('?')
    hold_urls = []
    all_repos = []
    for i in range(2, 21):
        hold_urls.append(split_url[0] + '?p=' + str(i) + '&' + split_url[1])
    for item in hold_urls:
        all_repos += get_the_repos(item)
    return all_repos

def scrape_github_data() -> List[Dict[str, str]]:
    """
    Loop through all of the repos and process them. Returns the processed data.
    """
    REPOS = ['zq99299/repository-summary',
 'CloudCompare/CloudCompare',
 'vispy/vispy',
 'mootools/mootools-core',
 'CodeMazeBlog/async-repository-dotnetcore-webapi',
 'AnemoneIndicum/taotao-repository',
 'gentoo/gentoo',
 'openstack/openstack',
 'scummvm/scummvm',
 'webpack/webpack.js.org',
 'magnayn/Jenkins-Repository',
 'WPO-Foundation/webpagetest',
 'octocat/Hello-World',
 'Torann/laravel-repository',
 'maduce/fosscad-repo',
 'angular/material-start',
 'a34546/Wei.Repository',
 'kaiyuanshe/repository',
 'wordpress-mobile/WordPress-iOS',
 'transmission/transmission',
 'slorber/gcm-server-repository',
 'tegon/clone-org-repos',
 'geometer/FBReaderJ',
 'Sage-Bionetworks/Synapse-Repository-Services',
 'jenkinsci/repository-connector-plugin',
 'zach-morris/repository.zachmorris',
 'geotools/geotools',
 'libjpeg-turbo/libjpeg-turbo',
 'HandBrake/HandBrake',
 'Auxilus/termux-x-repository',
 'toltec-dev/toltec',
 'HIGHWAY99/repository.thehighway',
 'esendir/MongoRepository',
 'prof-membrane/repository.membrane',
 'DSpace/xoai',
 'xiaoxiaoqingyi/mine-android-repository',
 'Azure-Samples/PartitionedRepository',
 'adlerpagliarini/RepositoryPattern-Dapper-EFCore',
 'Yara-Rules/rules',
 'racket/racket',
 'oamg/leapp-repository',
 'xmake-io/xmake-repo',
 'ErickWendel/generic-repository-nodejs-typescript-article',
 'cpina/github-action-push-to-another-repository',
 'rinvex/laravel-repositories',
 'openvinotoolkit/openvino',
 'ga4gh/data-repository-service-schemas',
 'popomore/projj',
 'ezsystems/repository-forms',
 'AllenDowney/ThinkBayes',
 'GoogleCloudPlatform/repository-gardener',
 'rlidwka/sinopia',
 'visminer/repositoryminer',
 'ecomfe/spec',
 'CastagnaIT/repository.castagnait',
 'xuezhijian/Spring-Demo-Repository',
 'yona-projects/yona',
 'packagemgmt/repositorytools',
 'Antergos/antergos-packages',
 'udacity/Sunshine-Version-2',
 'opencv/opencv_contrib',
 'offensive-security/exploitdb',
 'XvBMC/repository.xvbmc',
 'kisslinux/repo',
 'XiumingLee/MingRepository',
 'Kitware/CMake',
 'helm/chart-releaser',
 'pixta-dev/repository-mirroring-action',
 'doxygen/doxygen',
 'openscenegraph/OpenSceneGraph',
 'RedHatTraining/DO180-apps',
 'Rarst/release-belt',
 'IonicaBizau/repository-downloader',
 'layerfMRI/repository',
 'EgeBalci/Mass-Hacker-Arsenal',
 'rmccue/test-repository',
 'renfeng/android-repository',
 'aircrack-ng/aircrack-ng-archive',
 'pfsense/pfsense',
 'microsoft/WPF-Samples',
 'twosigma/git-meta',
 'winneon/tutorial-repository',
 'kodibae/repository.kodibae',
 'besnik/generic-repository',
 'ethereum/EIPs',
 'gperftools/gperftools',
 'samvera/active_fedora',
 'geoserver/geoserver',
 'zhaohehe/z-repository',
 'arch4edu/arch4edu',
 'simpligility/maven-repository-tools',
 'psalterio/repository',
 'cheeaun/repokemon',
 'I-Hope-Peace/ChangeDetectionRepository',
 'covenantkodi/repository.colossus',
 'DefinitelyTyped/DefinitelyTyped',
 'eddelbuettel/drat',
 'repology/repology-rules',
 'rdpeng/ProgrammingAssignment2',
 'glarizza/puppet_repository',
 'mateodelnorte/sourced-repo-mongo',
 'tesseract-ocr/tesseract',
 'botallen/repository.botallen',
 'sonatype-nexus-community/nexus-repository-composer',
 'recca0120/laravel-repository',
 'develar/settings-repository',
 'caffeinated/repository',
 'archlinuxcn/mirrorlist-repo',
 'sonatype-nexus-community/nexus-repository-apt',
 'dotnet/docs',
 'dcmi/repository',
 'dvorka/mindforger-repository',
 'sonatype-nexus-community/nexus-repository-helm',
 'renaudcerrato/appengine-maven-repository',
 'dotnet/core',
 'mateodelnorte/meta',
 'zendframework/zendframework',
 'mesosphere/universe',
 'kodi-community-addons/repository.marcelveldt',
 'sonatype-nexus-community/nexus-repository-import-scripts',
 'leonvanbokhorst/RepositoryPatternEntityFramework',
 'packal/repository',
 'jdf76/repository',
 'hacker-walker/repository',
 'drinfernoo/repository.example',
 'AdiChat/Repository-Hunter',
 'dobbelina/repository.dobbelina',
 'tugberkugurlu/GenericRepository',
 'alexandre-spieser/mongodb-generic-repository',
 'Guilouz/repository.guilouz',
 'jitsi/jitsi-maven-repository',
 'freeall/create-repository',
 'acoomans/ACCodeSnippetRepositoryPlugin',
 'singhsanket143/CppCompetitiveRepository',
 'omarabid/Self-Hosted-WordPress-Plugin-repository',
 'Vashiel/repository.adulthideout',
 'notepad-plus-plus/notepad-plus-plus',
 'crcms/repository',
 'scipy/scipy',
 'LeonWuV/FE-blog-repository',
 'DSpace/DSpace',
 'peter-evans/repository-dispatch',
 'JustryDeng/CommonRepository',
 'kisslinux/community',
 'Alfresco/alfresco-repository',
 'nasa/Common-Metadata-Repository',
 'vim/vim',
 'brunohbrito/MongoDB-RepositoryUoWPatterns',
 'ulyaoth/repository',
 'ziglibs/repository',
 'megamit/repository',
 'awes-io/repository',
 'green-fox-academy/git-lesson-repository',
 'thinkgem/repository',
 'darcyclarke/Repo.js',
 'repology/repology-updater',
 'Yet-Another-Series/Yet_Another_Algorithms_Repository',
 'OAI/OpenAPI-Specification',
 'touchgfx/touchgfx-open-repository',
 'technojam/Ultimate_Algorithms_Repository',
 'ioBroker/ioBroker.repositories',
 'philtabor/Youtube-Code-Repository',
 'dustinschultz/scf-config-repository',
 'RobThree/MongoRepository',
 'cnych/kubeapp',
 'grafana/grafana-plugin-repository',
 'dragonslayerx/Competitive-Programming-Repository',
 'nurkiewicz/spring-data-jdbc-repository',
 'magento-hackathon/composer-repository',
 'gamedilong/anes-repository',
 'collabH/repository',
 'kodi-czsk/repository',
 'sonatype/nexus-oss',
 'JustryDeng/PublicRepository',
 'GitIndonesia/awesome-indonesia-repo',
 'SharpRepository/SharpRepository',
 'jenkins-infra/repository-permissions-updater',
 'hadynz/repository.arabic.xbmc-addons',
 'Gexos/Hacking-Tools-Repository',
 'archlinuxcn/repo',
 'bosnadev/repository',
 'hassio-addons/repository',
 'sonatype/nexus-public',
 'andersao/l5-repository',
 'yiyang74262580/Repository',
 'matthewschrager/Repository',
 'ocaml/opam-repository',
 'sonatype/docker-nexus3',
 'puli/repository',
 'LuaDist/Repository',
 'OnsenUI/onsen.io',
 'AlexanderSharykin/RepositoryUtilities',
 'mzmine/mzmine2',
 'jackiekazil/data-wrangling',
 'haskell/hackage-server',
 'haskell/hackage-server',
 'mp2893/doctorai',
 'SwiftPackageIndex/PackageList',
 'openstreetmap/josm',
 'shihenw/convolutional-pose-machines-release',
 'ace-lectures/pattern-repository',
 'alanmcgovern/monotorrent',
 'PacktPublishing/Learning-PySpark',
 'traviscross/mtr',
 'deepmind/deepmind-research',
 'Sroy20/machine-learning-interview-questions',
 'x64dbg/docs',
 'thuehlinger/daemons',
 'fvwmorg/fvwm',
 'AlexanderSharykin/RepositoryUtilities',
 'OnsenUI/onsen.io',
 'grpc/grpc.io',
 'colcon/colcon-mixin-repository',
 'RIPE-NCC/whois',
 'glouppe/phd-thesis',
 'creative-computing-society/Hacktoberfest2020_CCS',
 'sous-chefs/nodejs',
 'Huawei/dockyard',
 'freeorion/freeorion',
 'sous-chefs/haproxy',
 'Rhombik/rhombik-object-repository',
 'vmware-tanzu/tgik',
 'ztrhgf/Powershell_CICD_repository',
 'jonatasbaldin/awesome-awesome-awesome',
 'nartc/nest-mean',
 'mateodelnorte/meta-npm',
 'reportportal/reportportal',
 'OpenScienceMOOC/Module-6-Open-Access-to-Research-Papers',
 'planetfederal/suite',
 'bitcoin-core/gui',
 'hibernate/hibernate-demos',
 'vrpn/vrpn',
 'chrisdee/Tools',
 'google/gitiles',
 'palominodb/PalominoDB-Public-Code-Repository',
 'djoos-cookbooks/newrelic',
 'miztiik/DevOps-Demos',
 'mp2893/med2vec',
 'components/jquery',
 'TRI-ML/packnet-sfm',
 'hiteshbpatel/Android_Blog_Projects',
 'vmware/open-vm-tools',
 'Flowpack/Flowpack.ElasticSearch.ContentRepositoryQueueIndexer',
 'arXivTimes/arXivTimes',
 'python-babel/babel',
 'gin-gonic/examples',
 'krazydanny/laravel-repository',
 'downthemall/downthemall-legacy',
 'ejwa/gitinspector',
 'CoreWCF/CoreWCF',
 'SOCI/soci',
 'foundeo/cfdocs',
 'sitemesh/sitemesh2',
 'foyzulkarim/GenericComponents',
 'OoliteProject/oolite',
 'fptudelft/FP101x-Content-2015',
 'host505/repository.host505',
 'razorpay/ifsc',
 'JoeyDeVries/LearnOpenGL',
 'danmunn/redmine_dmsf',
 'IseHayato/GitTestRepository',
 'winhu/MongoDB.Repository',
 'friendly-telegram/friendly-telegram',
 'asquarezone/AnsibleZone',
 'sous-chefs/nagios',
 'UNC-Libraries/Carolina-Digital-Repository',
 'sharpdx/SharpDX-Samples',
 'unitycontainer/unity',
 'Potential17/Hacktoberfest-2020',
 'libfann/fann',
 'foyzulkarim/GenericComponents',
 'VolodyaVechirko/RepositoryApp',
 'Wiznet/ioLibrary_Driver',
 'rg-engineering/ioBroker.heatingcontrol',
 'webanno/webanno',
 'sqlmapproject/udfhack',
 'mixu/gr',
 'akeneo/pim-community-dev',
 'jawi/ols',
 'nullism/clickingbad',
 'openpmix/openpmix',
 'brendt/settings-repository',
 'rhiever/Data-Analysis-and-Machine-Learning-Projects',
 'Brewtarget/brewtarget',
 'efreesen/active_repository',
 'disconnectme/disconnect-tracking-protection',
 'src-d/hercules',
 'ionic-team/ionic-bower',
 'flowable/flowable-examples',
 'georgy/nexus-npm-repository-plugin',
 'tier4/AutowareArchitectureProposal.iv',
 'xrootd/xrootd',
 'objcio/functional-swift',
 'mspnp/elasticsearch',
 'xinu-os/xinu',
 'fayland/dist-zilla-plugin-repository',
 'myopencart/ocStore',
 'Futureazoo/TextureRepository',
 'recalbox/recalbox-os',
 'objcode/v8',
 'chef-boneyard/database',
 'microsoft/moodle-repository_onenote',
 'w3c/csswg-test',
 'devit-tel/mongoose-repository',
 'QuickBlox/q-municate-ios',
 'CoskunKurtuldu/GenericRepositoryPattern',
 'chef-cookbooks/sudo',
 'tomgi/git_stats',
 'Finesse/web-fonts-repository',
 'supermamon/Reposi3',
 'tv42/gitosis',
 'duorg/Scripts',
 'fluent/fluentd-docs',
 'RocketChat/Docker.Official.Image',
 'PHPFusion/PHPFusion',
 'sous-chefs/tomcat',
 'TelerikAcademy/HTML',
 'sous-chefs/apt',
 'Harvard-IACS/2018-CS109A',
 'Yenthe666/Odoo_Samples',
 'boochtek/activerecord-repository',
 'sexym0nk3y/Laravel-5.3-Repository',
 'backmeupplz/voicy',
 'xroche/httrack',
 'Shougo/neosnippet-snippets',
 'lensfun/lensfun',
 'LGalaxiesPublicRelease/LGalaxies_PublicRepository',
 'dspinellis/awesome-msr',
 'rudrakshpathak/laravel-service-repository-pattern',
 'hacs/default',
 'chaotic-aur/infra',
 'DaveGut/DEPRECATED-TP-Link-SmartThings',
 'SkinsRestorer/SkinsRestorerX',
 'buddhi1980/mandelbulber2',
 'kubeflow/examples',
 'Azure/azure-policy',
 'exvim/main',
 'OWASP/owasp.github.io',
 'hraban/tomono',
 'ElmerCSC/elmerfem']

    return [process_repo(repo) for repo in REPOS]


def get_repo_data(cached=False):
    '''
    This function reads in repo data from github database and writes data to
    a csv file if cached == False or if cached == True reads in repo df from
    a csv file, returns df.
    '''
    if cached == False or os.path.isfile('repo_data.csv') == False:
        
        # Read fresh data from db into a DataFrame.
        df = pd.DataFrame(scrape_github_data())
        
        # Write DataFrame to a csv file.
        df.to_csv('repo_data.csv')
        
    else:
        
        # If csv file exists or cached == True, read in data from csv.
        df = pd.read_csv('repo_data.csv', index_col=1)
        
    return df
