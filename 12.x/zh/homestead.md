
# Laravel Homestead

-   [介绍](#%E4%BB%8B%E7%BB%8D)
-   [安装与设置](#%E5%AE%89%E8%A3%85%E4%B8%8E%E8%AE%BE%E7%BD%AE)
    -   [第一步](#%E7%AC%AC%E4%B8%80%E6%AD%A5)
    -   [配置 Homestead](#%E9%85%8D%E7%BD%AE-homestead)
    -   [配置 Nginx 站点](#%E9%85%8D%E7%BD%AE-nginx-%E7%AB%99%E7%82%B9)
    -   [配置服务](#%E9%85%8D%E7%BD%AE%E6%9C%8D%E5%8A%A1)
    -   [启动 Vagrant Box](#%E5%90%AF%E5%8A%A8-vagrant-box)
    -   [按项目安装](#%E6%8C%89%E9%A1%B9%E7%9B%AE%E5%AE%89%E8%A3%85)
    -   [安装可选功能](#%E5%AE%89%E8%A3%85%E5%8F%AF%E9%80%89%E5%8A%9F%E8%83%BD)
    -   [别名](#%E5%88%AB%E5%90%8D)
-   [更新 Homestead](#%E6%9B%B4%E6%96%B0-homestead)
-   [日常使用](#%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8)
    -   [通过 SSH 连接](#%E9%80%9A%E8%BF%87-ssh-%E8%BF%9E%E6%8E%A5)
    -   [添加额外的站点](#%E6%B7%BB%E5%8A%A0%E9%A2%9D%E5%A4%96%E7%9A%84%E7%AB%99%E7%82%B9)
    -   [环境变量](#%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F)
    -   [端口](#%E7%AB%AF%E5%8F%A3)
    -   [PHP 版本](#php-%E7%89%88%E6%9C%AC)
    -   [连接数据库](#%E8%BF%9E%E6%8E%A5%E6%95%B0%E6%8D%AE%E5%BA%93)
    -   [数据库备份](#%E6%95%B0%E6%8D%AE%E5%BA%93%E5%A4%87%E4%BB%BD)
    -   [配置 Cron 调度](#%E9%85%8D%E7%BD%AE-cron-%E8%B0%83%E5%BA%A6)
    -   [配置 Mailpit](#%E9%85%8D%E7%BD%AE-mailpit)
    -   [配置 Minio](#%E9%85%8D%E7%BD%AE-minio)
    -   [Laravel Dusk](#laravel-dusk)
    -   [共享你的环境](#%E5%85%B1%E4%BA%AB%E4%BD%A0%E7%9A%84%E7%8E%AF%E5%A2%83)
-   [调试与性能分析](#%E8%B0%83%E8%AF%95%E4%B8%8E%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90)
    -   [使用 Xdebug 调试 Web 请求](#%E4%BD%BF%E7%94%A8-xdebug-%E8%B0%83%E8%AF%95-web-%E8%AF%B7%E6%B1%82)
    -   [调试 CLI 应用](#%E8%B0%83%E8%AF%95-cli-%E5%BA%94%E7%94%A8)
    -   [使用 Blackfire 分析应用性能](#%E4%BD%BF%E7%94%A8-blackfire-%E5%88%86%E6%9E%90%E5%BA%94%E7%94%A8%E6%80%A7%E8%83%BD)
-   [网络接口](#%E7%BD%91%E7%BB%9C%E6%8E%A5%E5%8F%A3)
-   [扩展 Homestead](#%E6%89%A9%E5%B1%95-homestead)
-   [特定提供商设置](#%E7%89%B9%E5%AE%9A%E6%8F%90%E4%BE%9B%E5%95%86%E8%AE%BE%E7%BD%AE)
    -   [VirtualBox](#virtualbox)

## 介绍

Laravel 致力于让整个 PHP 开发体验变得愉快，其中也包括你的本地开发环境。[Laravel Homestead](https://github.com/laravel/homestead?utm_source=chatgpt.com) 是一个官方预打包的 Vagrant box，它为你提供了一个极佳的开发环境，而无需在本地机器上安装 PHP、Web 服务器或任何其他服务器软件。

[Vagrant](https://www.vagrantup.com?utm_source=chatgpt.com) 提供了一种简单、优雅的方式来管理和配置虚拟机。Vagrant box 完全是一次性的。如果出现问题，你可以在几分钟内销毁并重新创建这个 box！

Homestead 可以运行在任何 Windows、macOS 或 Linux 系统上，并且包含 Nginx、PHP、MySQL、PostgreSQL、Redis、Memcached、Node 以及开发出色 Laravel 应用所需的所有其他软件。

> [!警告]
> 如果你使用的是 Windows，可能需要启用硬件虚拟化（VT-x）。这通常可以通过 BIOS 启用。如果你在 UEFI 系统上使用 Hyper-V，则可能还需要禁用 Hyper-V 才能访问 VT-x。



### Included Software

<style>
    #software-list > ul {
        column-count: 2; -moz-column-count: 2; -webkit-column-count: 2;
        column-gap: 5em; -moz-column-gap: 5em; -webkit-column-gap: 5em;
        line-height: 1.9;
    }
</style>

<div id="software-list" markdown="1">

- Ubuntu 22.04
- Git
- PHP 8.3
- PHP 8.2
- PHP 8.1
- PHP 8.0
- PHP 7.4
- PHP 7.3
- PHP 7.2
- PHP 7.1
- PHP 7.0
- PHP 5.6
- Nginx
- MySQL 8.0
- lmm
- Sqlite3
- PostgreSQL 15
- Composer
- Docker
- Node (With Yarn, Bower, Grunt, and Gulp)
- Redis
- Memcached
- Beanstalkd
- Mailpit
- avahi
- ngrok
- Xdebug
- XHProf / Tideways / XHGui
- wp-cli

</div>

### 可选软件

<style>
    #software-list > ul {
        column-count: 2; -moz-column-count: 2; -webkit-column-count: 2;
        column-gap: 5em; -moz-column-gap: 5em; -webkit-column-gap: 5em;
        line-height: 1.9;
    }
</style>

<div id="software-list" markdown="1">

- Apache
- Blackfire
- Cassandra
- Chronograf
- CouchDB
- Crystal & Lucky Framework
- Elasticsearch
- EventStoreDB
- Flyway
- Gearman
- Go
- Grafana
- InfluxDB
- Logstash
- MariaDB
- Meilisearch
- MinIO
- MongoDB
- Neo4j
- Oh My Zsh
- Open Resty
- PM2
- Python
- R
- RabbitMQ
- Rust
- RVM (Ruby Version Manager)
- Solr
- TimescaleDB
- Trader <small>(PHP extension)</small>
- Webdriver & Laravel Dusk Utilities

</div>

## 安装与设置

### 第一步

在启动你的 Homestead 环境之前，你必须先安装 [Vagrant](https://developer.hashicorp.com/vagrant/downloads?utm_source=chatgpt.com)，以及以下受支持的提供商之一：

-   [VirtualBox 6.1.x](https://www.virtualbox.org/wiki/Download_Old_Builds_6_1?utm_source=chatgpt.com)
-   [Parallels](https://www.parallels.com/products/desktop/?utm_source=chatgpt.com)

这些软件包都为所有流行的操作系统提供了易于使用的可视化安装程序。



要使用 **Parallels provider**，你需要安装 [Parallels Vagrant 插件](https://github.com/Parallels/vagrant-parallels?utm_source=chatgpt.com)。它是免费的。

#### 安装 Homestead

你可以通过将 Homestead 仓库克隆到主机上来安装 Homestead。建议将仓库克隆到你的 **用户目录**（home 目录）下的 `Homestead` 文件夹中，因为 Homestead 虚拟机会作为你所有 Laravel 应用的宿主环境。在本文档中，我们会将这个目录称为 **Homestead 目录**：

```shell
git clone https://github.com/laravel/homestead.git ~/Homestead
```

克隆完 Laravel Homestead 仓库后，你需要切换到 `release` 分支。这个分支始终包含 Homestead 的最新稳定版本：

```shell
cd ~/Homestead

git checkout release
```

接下来，在 Homestead 目录中执行 `bash init.sh` 命令来创建 `Homestead.yaml` 配置文件。`Homestead.yaml` 文件是你配置 Homestead 安装的地方。该文件会被放置在 Homestead 目录下：

```shell
# macOS / Linux...
bash init.sh

# Windows...
init.bat
```

### 配置 Homestead

#### 设置 Provider

`Homestead.yaml` 文件中的 `provider` 键表示应该使用哪个 Vagrant provider：`virtualbox` 或 `parallels`：

    provider: virtualbox

> [!警告]
> 如果你使用的是 Apple Silicon，则必须使用 Parallels provider。

#### 配置共享文件夹

`Homestead.yaml` 文件中的 `folders` 属性列出了你希望与 Homestead 环境共享的所有文件夹。 当这些文件夹中的文件发生变化时，它们会在本地机器和 Homestead 虚拟环境之间保持同步。你可以根据需要配置任意多个共享文件夹：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
```

> [!警告]
> Windows 用户不应该使用 `~/` 路径语法，而应当使用项目的完整路径，例如：
`C:\Users\user\Code\project1`



你应该始终将**每个应用程序单独映射到它自己的文件夹**，而不是把包含所有应用的大目录一次性映射进去。
当你映射一个文件夹时，虚拟机必须追踪该文件夹内 **每一个文件** 的磁盘 IO。
如果文件夹中文件数量庞大，可能会导致性能下降：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
    - map: ~/code/project2
      to: /home/vagrant/project2
```

> [!警告]
> 使用 Homestead 时，绝对不要挂载 `.`（当前目录）。
> 这样会导致 Vagrant 不会把当前目录映射到 `/vagrant`，从而破坏可选功能，并在配置时产生意外结果。

要启用 [NFS](https://developer.hashicorp.com/vagrant/docs/synced-folders/nfs?utm_source=chatgpt.com)，你可以在文件夹映射中添加一个 `type` 选项：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
      type: "nfs"
```

> [!警告]
> 在 Windows 上使用 NFS 时，建议安装 [vagrant-winnfsd](https://github.com/winnfsd/vagrant-winnfsd?utm_source=chatgpt.com) 插件。
> 这个插件会确保 Homestead 虚拟机中的文件和目录保持正确的用户/组权限。

你还可以通过在 `options` 键下列出配置，传递 Vagrant 的 [Synced Folders](https://developer.hashicorp.com/vagrant/docs/synced-folders/basic_usage?utm_source=chatgpt.com) 所支持的任意选项：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
      type: "rsync"
      options:
          rsync__args: ["--verbose", "--archive", "--delete", "-zz"]
          rsync__exclude: ["node_modules"]
```

### 配置 Nginx 站点

对 Nginx 不熟悉？没关系。
`Homestead.yaml` 文件中的 `sites` 属性允许你轻松地将一个“域名”映射到 Homestead 环境中的某个文件夹。
`Homestead.yaml` 文件中已经包含了一个示例站点配置。
同样地，你可以根据需要在 Homestead 环境中添加任意数量的站点。
Homestead 可以作为一个方便的虚拟化环境，为你正在开发的每个 Laravel 应用提供服务：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
```



如果你在配置 Homestead 虚拟机之后更改了 `sites` 属性，你应该在终端中执行 `vagrant reload --provision` 命令来更新虚拟机上的 Nginx 配置。

> [!警告]
> Homestead 脚本被构建为尽可能幂等。然而，如果你在配置时遇到问题，你应该通过执行 `vagrant destroy && vagrant up` 命令来销毁并重建虚拟机。

#### 主机名解析

Homestead 使用 `mDNS` 发布主机名以进行自动主机解析。
如果你在 `Homestead.yaml` 文件中设置 `hostname: homestead`，该主机将在 `homestead.local` 可用。
macOS、iOS 和 Linux 桌面发行版默认包含 `mDNS` 支持。
如果你使用 Windows，你必须安装 [Bonjour Print Services for Windows](https://support.apple.com/kb/DL999?viewlocale=en_US&locale=en_US&utm_source=chatgpt.com)。

使用自动主机名在 [按项目安装](#per-project-installation) Homestead 时效果最好。
如果你在单个 Homestead 实例上托管多个站点，你可以将网站的“域名”添加到你机器的 `hosts` 文件中。
`hosts` 文件会将对你的 Homestead 站点的请求重定向到你的 Homestead 虚拟机。

-   在 macOS 和 Linux 上，这个文件位于 `/etc/hosts`。

-   在 Windows 上，这个文件位于 `C:\Windows\System32\drivers\etc\hosts`。

你添加到这个文件的行看起来像这样：

```text
192.168.56.56  homestead.test
```

确保所列出的 IP 地址是你在 `Homestead.yaml` 文件中设置的那个。
一旦你将域名添加到 `hosts` 文件并启动 Vagrant box，你将能够通过浏览器访问该站点：

```shell
http://homestead.test
```



### 配置服务

Homestead 默认启动若干服务；然而，你可以在配置（provisioning）期间自定义哪些服务被启用或禁用。例如，你可以通过修改 `Homestead.yaml` 文件中的 `services` 选项来启用 PostgreSQL 并禁用 MySQL：

```yaml
services:
    - enabled:
        - "postgresql"
    - disabled:
        - "mysql"
```

指定的服务将根据它们在 `enabled` 和 `disabled` 指令中的顺序被启动或停止。

### 启动 Vagrant Box

一旦你按自己的喜好编辑了 `Homestead.yaml`，在你的 Homestead 目录中运行 `vagrant up` 命令。Vagrant 将启动虚拟机并自动配置你的共享文件夹和 Nginx 站点。

要销毁该机器，你可以使用 `vagrant destroy` 命令。

### 按项目安装

你可以选择不在全局安装 Homestead 并在所有项目之间共享相同的 Homestead 虚拟机，而是为你管理的每个项目配置一个 Homestead 实例。如果你希望随项目一起发布 `Vagrantfile`，以便其他协作者在克隆项目仓库后能够立即运行 `vagrant up`，则按项目安装 Homestead 可能更有益。

你可以使用 Composer 包管理器将 Homestead 安装到你的项目中：

```shell
composer require laravel/homestead --dev
```

一旦 Homestead 被安装，调用 Homestead 的 `make` 命令为你的项目生成 `Vagrantfile` 和 `Homestead.yaml` 文件。这些文件将被放置在你的项目根目录。`make` 命令会自动在 `Homestead.yaml` 文件中配置 `sites` 和 `folders` 指令：

```shell
# macOS / Linux...
php vendor/bin/homestead make

# Windows...
vendor\\bin\\homestead make
```



接下来，在终端中运行 `vagrant up` 命令，并在浏览器中通过 `http://homestead.test` 访问你的项目。
请记住，如果你没有使用自动的 [主机名解析](#hostname-resolution)，仍然需要在 `/etc/hosts` 文件中添加 `homestead.test` 或你选择的域名条目。

### 安装可选功能（Installing Optional Features）

可选软件可以通过 `Homestead.yaml` 文件中的 `features` 选项进行安装。
大多数功能可以通过布尔值开启或关闭，而某些功能允许配置多个选项：

```yaml
features:
    - blackfire:
        server_id: "server_id"
        server_token: "server_value"
        client_id: "client_id"
        client_token: "client_value"
    - cassandra: true
    - chronograf: true
    - couchdb: true
    - crystal: true
    - dragonflydb: true
    - elasticsearch:
        version: 7.9.0
    - eventstore: true
        version: 21.2.0
    - flyway: true
    - gearman: true
    - golang: true
    - grafana: true
    - influxdb: true
    - logstash: true
    - mariadb: true
    - meilisearch: true
    - minio: true
    - mongodb: true
    - neo4j: true
    - ohmyzsh: true
    - openresty: true
    - pm2: true
    - python: true
    - r-base: true
    - rabbitmq: true
    - rustc: true
    - rvm: true
    - solr: true
    - timescaledb: true
    - trader: true
    - webdriver: true
```

#### Elasticsearch

你可以指定 Elasticsearch 的支持版本，必须使用完整版本号（主版本.次版本.修订号）。
默认安装会创建一个名为 `homestead` 的集群。
请注意，Elasticsearch **不应使用操作系统超过一半的内存**，因此确保 Homestead 虚拟机至少有 Elasticsearch 分配内存的两倍。

> [!注意]
> 请参考 [Elasticsearch 文档](https://www.elastic.co/guide/en/elasticsearch/reference/current) 了解如何自定义配置。



<a name="mariadb"></a>
#### MariaDB

启用 MariaDB 将移除 MySQL 并安装 MariaDB。MariaDB 通常可作为 MySQL 的直接替代品，因此在应用的数据库配置中仍应使用 `mysql` 数据库驱动。

<a name="mongodb"></a>
#### MongoDB

默认的 MongoDB 安装会将数据库用户名设置为 `homestead` ，对应密码为 `secret`.

<a name="neo4j"></a>
#### Neo4j

默认的 Neo4j 安装会将数据库用户名设置为 `homestead` ，对应密码为 `secret`。要访问 Neo4j 浏览器，请通过网页浏览器访问 `http://homestead.test:7474` 。端口 `7687` (Bolt), `7474` (HTTP), 和 `7473` (HTTPS) 已准备就绪，可处理来自 Neo4j 客户端的请求。

<a name="aliases"></a>
### 别名

您可以通过修改 Homestead 目录中的 `aliases` 文件来为 Homestead 虚拟机添加 Bash 别名：

```shell
alias c='clear'
alias ..='cd ..'
```

更新 `aliases` 文件后，应使用 `vagrant reload --provision` 命令重新配置 Homestead 虚拟机。这将确保新别名在虚拟机上可用。

<a name="updating-homestead"></a>
## 更新 Homestead

在开始更新 Homestead 之前，应确保已通过以下命令移除当前虚拟机（在 Homestead 目录中执行）：

```shell
vagrant destroy
```

接下来，需要更新 Homestead 源代码。如果您克隆了仓库，可以在最初克隆仓库的位置执行以下命令：

```shell
git fetch

git pull origin release
```

这些命令将从 GitHub 仓库拉取最新的 Homestead 代码，获取最新标签，然后检出最新的标签版本。您可以在 Homestead 的 [GitHub 发布页面](https://github.com/laravel/homestead/releases)上找到最新的稳定发布版本。



如果您通过项目的 `composer.json` 文件安装了 Homestead，应确保 `composer.json` 文件中包含 `"laravel/homestead": "^12"` 并更新依赖项：

```shell
composer update
```

接下来，应使用 `vagrant box update` 命令更新 Vagrant 盒子：

```shell
vagrant box update
```

更新 Vagrant 盒子后，应在 Homestead 目录中运行 `bash init.sh` 命令以更新 Homestead 的附加配置文件。系统将询问您是否要覆盖现有的 `Homestead.yaml`, `after.sh`, 和 `aliases` 文件：

```shell
# macOS / Linux...
bash init.sh

# Windows...
init.bat
```

最后，需要重新生成 Homestead 虚拟机以使用最新的 Vagrant 安装：

```shell
vagrant up
```

<a name="daily-usage"></a>
## 日常使用

<a name="connecting-via-ssh"></a>
### 通过 SSH 连接

您可以在 Homestead 目录中执行 `vagrant ssh` 终端命令来 SSH 连接到虚拟机。

<a name="adding-additional-sites"></a>
### 添加额外站点

Homestead 环境配置并运行后，您可能希望为其他 Laravel 项目添加额外的 Nginx 站点。您可以在单个 Homestead 环境中运行任意数量的 Laravel 项目。要添加额外站点，请将站点添加到 `Homestead.yaml` 文件中。

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
    - map: another.test
      to: /home/vagrant/project2/public
```

> [!警告]
> 在添加站点之前，应确保已为项目目录配置了 [文件夹映射](#configuring-shared-folders) 。

如果 Vagrant 没有自动管理您的 "hosts" 文件，您可能还需要将新站点添加到该文件中。在 macOS 和 Linux 上，该文件位于 `/etc/hosts`。在 Windows 上，位于 `C:\Windows\System32\drivers\etc\hosts`:

```text
192.168.56.56  homestead.test
192.168.56.56  another.test
```



添加站点后，在 Homestead 目录中执行 `vagrant reload --provision` 终端命令。

<a name="site-types"></a>
#### 站点类型

Homestead 支持多种站点"类型"，便于运行非 Laravel 项目。例如，我们可以使用 `statamic` 站点类型轻松将 Statamic 应用添加到 Homestead：

```yaml
sites:
    - map: statamic.test
      to: /home/vagrant/my-symfony-project/web
      type: "statamic"
```

可用的站点类型包括： `apache`, `apache-proxy`, `apigility`, `expressive`, `laravel` (默认), `proxy` 用于 nginx）, `silverstripe`, `statamic`, `symfony2`, `symfony4`, 和 `zf`。

<a name="site-parameters"></a>
#### 站点参数

您可以通过 `fastcgi_param` 站点指令为站点添加额外的 Nginx `params` 值：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
      params:
          - key: FOO
            value: BAR
```

<a name="environment-variables"></a>
### 环境变量

您可以通过在 `Homestead.yaml` 文件中添加全局环境变量：

```yaml
variables:
    - key: APP_ENV
      value: local
    - key: FOO
      value: bar
```

更新 `Homestead.yaml` 文件后，务必通过执行 `vagrant reload --provision` 命令重新配置虚拟机。这将更新所有已安装 PHP 版本的 PHP-FPM 配置，同时更新 `vagrant` 用户的环境。

<a name="ports"></a>
### Ports

默认情况下，以下端口会转发到您的 Homestead 环境：
<div class="content-list" markdown="1">

- **HTTP:** 8000 &rarr; 转发到 80
- **HTTPS:** 44300 &rarr; 转发到 443

</div>

<a name="forwarding-additional-ports"></a>
#### 转发额外端口

如需将额外端口转发到 Vagrant 盒子，可以在 `ports` 文件中定义 `Homestead.yaml` 配置项。更新 `Homestead.yaml` 文件后，务必通过执行 `vagrant reload --provision` 命令重新配置虚拟机：

```yaml
ports:
    - send: 50000
      to: 5000
    - send: 7777
      to: 777
      protocol: udp
```



以下列出了您可能希望从主机映射到 Vagrant 盒子的其他 Homestead 服务端口：

<div class="content-list" markdown="1">

- **SSH:** 2222 &rarr; 到 22
- **ngrok UI:** 4040 &rarr; 到 4040
- **MySQL:** 33060 &rarr; 到 3306
- **PostgreSQL:** 54320 &rarr; 到 5432
- **MongoDB:** 27017 &rarr; 到 27017
- **Mailpit:** 8025 &rarr; 到 8025
- **Minio:** 9600 &rarr; 到 9600

</div>

<a name="php-versions"></a>
### PHP 版本

Homestead 支持在同一虚拟机上运行多个 PHP 版本。您可以在 `Homestead.yaml` 文件中为指定站点设置要使用的 PHP 版本。可用的 PHP 版本包括： "5.6", "7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1", "8.2", 和 "8.3", (默认版本):

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
      php: "7.1"
```

[在 Homestead 虚拟机内](#connecting-via-ssh), 您可以通过 CLI 使用任何受支持的 PHP 版本：

```shell
php5.6 artisan list
php7.0 artisan list
php7.1 artisan list
php7.2 artisan list
php7.3 artisan list
php7.4 artisan list
php8.0 artisan list
php8.1 artisan list
php8.2 artisan list
php8.3 artisan list
```

您可以通过在 Homestead 虚拟机内执行以下命令来更改 CLI 使用的默认 PHP 版本：

```shell
php56
php70
php71
php72
php73
php74
php80
php81
php82
php83
```

<a name="connecting-to-databases"></a>
### 连接数据库

系统已为 MySQL 和 PostgreSQL 配置了 `homestead` 数据库。要从主机的数据库客户端连接到 MySQL 或 PostgreSQL 数据库，应连接到 `127.0.0.1` 的 `33060` 端口（MySQL）或 `54320` 端口（PostgreSQL）。两个数据库的用户名和密码均为 `homestead` / `secret`.

> [!警告]
> 仅当从主机连接数据库时才应使用这些非标准端口。在 Laravel 应用的 `database` 配置文件中，您将使用默认的 3306 和 5432 端口，因为 Laravel 运行在虚拟机_内部_。



### 数据库备份（Database Backups）

Homestead 可以在你的 Homestead 虚拟机被销毁时自动备份你的数据库。
要使用此功能，你必须使用 **Vagrant 2.1.0 或更高版本**。
或者，如果你使用的是更旧版本的 Vagrant，则必须安装 `vagrant-triggers` 插件。
要启用自动数据库备份，请在你的 `Homestead.yaml` 文件中添加下面这一行：

```yaml
backup: true
```

完成配置后，当执行 `vagrant destroy` 命令时，Homestead 会将你的数据库导出到 `.backup/mysql_backup` 和 `.backup/postgres_backup` 目录。
这些目录可以在你安装 Homestead 的文件夹中找到，或者如果你使用的是 [per project installation](#per-project-installation)（按项目安装）方式，则在你的项目根目录中找到。

### 配置 Cron 调度（Configuring Cron Schedules）

Laravel 提供了一种便捷方式，通过调度每分钟运行一次的 `schedule:run` Artisan 命令来[调度 Cron 任务](/docs/laravel/12.x/scheduling)。
`schedule:run` 命令会检查你 `routes/console.php` 文件中定义的任务调度，以确定要运行哪些计划任务（scheduled tasks）。

如果你希望在某个 Homestead 站点中运行 `schedule:run` 命令，你可以在定义站点时，将 `schedule` 选项设置为 `true`：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
      schedule: true
```

该站点的 Cron 任务将会在 Homestead 虚拟机的 `/etc/cron.d` 目录中被定义。

### 配置 Mailpit（Configuring Mailpit）

[Mailpit](https://github.com/axllent/mailpit) 允许你拦截（intercept）发出的邮件并进行检查，而不会真正将邮件发送给收件人。
要开始使用，请更新你的应用的 `.env` 文件，使用下面的邮件配置：

```ini
MAIL_MAILER=smtp
MAIL_HOST=localhost
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
```



在完成 Mailpit 配置后，你可以通过访问 `http://localhost:8025` 来进入 Mailpit 仪表盘（dashboard）。

### 配置 Minio（Configuring Minio）

[Minio](https://github.com/minio/minio) 是一个开源的对象存储服务器，并且提供与 Amazon S3 兼容的 API。
要安装 Minio，请在 `Homestead.yaml` 文件的 [features](#installing-optional-features)（可选功能）部分添加下面的配置选项：

    minio: true

默认情况下，Minio 运行在 **9600 端口**。
你可以通过访问 `http://localhost:9600` 来进入 Minio 控制面板（control panel）。
默认的 Access Key（访问密钥）是 `homestead`，默认的 Secret Key（秘密密钥）是 `secretkey`。
在访问 Minio 时，你应始终使用 region（区域）`us-east-1`。

要使用 Minio，请确保你的 `.env` 文件包含下面的配置项：

```ini
AWS_USE_PATH_STYLE_ENDPOINT=true
AWS_ENDPOINT=http://localhost:9600
AWS_ACCESS_KEY_ID=homestead
AWS_SECRET_ACCESS_KEY=secretkey
AWS_DEFAULT_REGION=us-east-1
```

要创建由 Minio 提供支持的 “S3” Bucket（存储桶），请在 `Homestead.yaml` 文件中添加 `buckets` 指令。
在定义 Bucket 之后，你需要在终端中执行 `vagrant reload --provision` 命令：

```yaml
buckets:
    - name: your-bucket
      policy: public
    - name: your-private-bucket
      policy: none
```

支持的 `policy`（策略）值包括：`none`、`download`、`upload` 和 `public`。

### Laravel Dusk

要在 Homestead 中运行 [Laravel Dusk](/docs/laravel/12.x/dusk) 测试，你应当在 Homestead 配置中启用 [webdriver 功能](#installing-optional-features)：

```yaml
features:
    - webdriver: true
```

启用 `webdriver` 功能后，你需要在终端中执行 `vagrant reload --provision` 命令。

### 共享你的环境（Sharing Your Environment）

有时你可能希望将你当前正在进行的工作共享给同事（coworkers）或客户（client）。
Vagrant 通过 `vagrant share` 命令提供了内置支持来实现这一点；
但是，如果你在 `Homestead.yaml` 文件中配置了**多个站点（sites）**，此功能将无法工作。



为了**解决这个问题**，Homestead 提供了它自己的 `share` 命令。
要开始使用，请通过 `vagrant ssh` [SSH 进入你的 Homestead 虚拟机](#connecting-via-ssh)，然后执行 `share homestead.test` 命令。
该命令会共享你 `Homestead.yaml` 配置文件中的 `homestead.test` 站点。
你也可以将 `homestead.test` 替换为你配置的任何其他站点：

```shell
share homestead.test
```

运行该命令后，你会看到一个 **Ngrok 界面**出现，其中包含 activity log（活动日志）以及该共享站点的**可公开访问的 URL**。
如果你希望指定自定义的 region（区域）、subdomain（子域）或其他 Ngrok 运行时选项，你可以将它们添加到 `share` 命令中：

```shell
share homestead.test -region=eu -subdomain=laravel
```

如果你需要使用 **HTTPS 共享内容**而不是 HTTP，则使用 `sshare` 命令替代 `share` 即可实现。

> [!警告]
> 记住，Vagrant 本质上是不安全的，并且当执行 `share` 命令时，你是在将你的虚拟机暴露到互联网。

## 调试与性能分析（Debugging and Profiling）

### 使用 Xdebug 调试 Web 请求（Debugging Web Requests With Xdebug）

Homestead 包含对逐步调试（step debugging）的支持，使用的是 [Xdebug](https://xdebug.org)。
例如，你可以在浏览器中访问一个页面，PHP 将会连接到你的 IDE，从而允许对正在运行的代码进行检查（inspection）和修改。

默认情况下，Xdebug 已经在运行，并且已准备好接受连接。
如果你需要在 CLI（命令行）中启用 Xdebug，请在你的 Homestead 虚拟机内执行 `sudo phpenmod xdebug` 命令。
接下来，按照你的 IDE 的指示启用调试。
最后，配置你的浏览器，通过扩展或 [bookmarklet](https://www.jetbrains.com/phpstorm/marklets/) 触发 Xdebug。

> [!警告]
> Xdebug 会导致 PHP 运行显著变慢。要禁用 Xdebug，请在你的 Homestead 虚拟机内运行 `sudo phpdismod xdebug`，并重启 FPM（PHP-FPM）服务。



#### 自动启动 Xdebug

在调试会向 Web 服务器发起请求的功能测试时，自动启动调试会比修改测试代码、传递自定义 Header 或 Cookie 以触发调试更加方便。
要强制 Xdebug 自动启动，请在 Homestead 虚拟机中修改 `/etc/php/7.x/fpm/conf.d/20-xdebug.ini` 文件，并添加以下配置：

```ini
; 如果 Homestead.yaml 为 IP 地址配置了不同的子网，该地址可能会有所不同……
xdebug.client_host = 192.168.10.1
xdebug.mode = debug
xdebug.start_with_request = yes
```

### 调试 CLI（命令行）应用程序

要调试 PHP CLI 应用程序，请在 Homestead 虚拟机中使用 `xphp` Shell（终端）别名：

```shell
xphp /path/to/script
```

### 使用 Blackfire 进行应用性能分析

[Blackfire](https://blackfire.io/docs/introduction) 是一个用于分析（profiling）Web 请求和 CLI（命令行）应用的服务。它提供交互式用户界面，可通过调用图（call-graphs）和时间线（timelines）来展示分析数据。Blackfire 适用于开发、预发布（staging）以及生产环境，并且不会对最终用户产生任何性能开销（overhead）。此外，Blackfire 还能对代码及 `php.ini` 配置项进行性能、质量和安全检查。

[Blackfire Player](https://blackfire.io/docs/player/index) 是一个开源的 Web 爬取（Crawling）、Web 测试（Testing）和 Web 抓取（Scraping）工具，可与 Blackfire 协同工作，用于编写脚本化的 profiling（性能分析）场景。

要启用 Blackfire，请在 Homestead 配置文件中使用 `"features"` 设置：

```yaml
features:
    - blackfire:
        server_id: "server_id"
        server_token: "server_value"
        client_id: "client_id"
        client_token: "client_value"
```



Blackfire 的服务器凭据（server credentials）和客户端凭据（client credentials）**需要 Blackfire 账户**，请访问：[注册 Blackfire 账户](https://blackfire.io/signup)。Blackfire 提供多种分析（profile）应用的方式，包括 CLI（命令行）工具和浏览器扩展插件。请[查阅 Blackfire 文档了解更多详情](https://blackfire.io/docs/php/integrations/laravel/index)。

## 网络接口（Network Interfaces）

`Homestead.yaml` 文件中的 `networks` 属性用于为你的 Homestead 虚拟机配置网络接口。你可以根据需要配置任意数量的网络接口：

```yaml
networks:
    - type: "private_network"
      ip: "192.168.10.20"
```

要启用[桥接（bridged）](https://developer.hashicorp.com/vagrant/docs/networking/public_network)网络接口，请在网络配置中设置 `bridge` 选项，并将网络类型更改为 `public_network`：

```yaml
networks:
    - type: "public_network"
      ip: "192.168.10.20"
      bridge: "en1: Wi-Fi (AirPort)"
```

要启用 [DHCP](https://developer.hashicorp.com/vagrant/docs/networking/public_network#dhcp)，只需在配置中移除 `ip` 选项即可：

```yaml
networks:
    - type: "public_network"
      bridge: "en1: Wi-Fi (AirPort)"
```

要修改网络所使用的设备（device），你可以在网络配置中添加 `dev` 选项。默认的 `dev` 值为 `eth0`：

```yaml
networks:
    - type: "public_network"
      ip: "192.168.10.20"
      bridge: "en1: Wi-Fi (AirPort)"
      dev: "enp2s0"
```


## 扩展 Homestead（Extending Homestead）

你可以在 Homestead 目录根路径下的 `after.sh` 脚本中扩展 Homestead。在该文件中，你可以添加任何用于正确配置和自定义虚拟机所需的 Shell 命令。

在自定义 Homestead 时，Ubuntu 可能会询问你是要保留软件包的原始配置，还是使用新的配置文件覆盖它。为了避免这种情况，你应该在安装软件包时使用以下命令，以防止覆盖 Homestead 之前写入的任何配置：

```shell
sudo apt-get -y \
    -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" \
    install package-name
```



### 用户自定义（User Customizations）

当你在团队中使用 Homestead 时，你可能希望调整（tweak）Homestead，使其更符合你个人的开发风格。要实现这一点，你可以在 Homestead 目录的根路径下创建 `user-customizations.sh` 文件（也就是包含 `Homestead.yaml` 的同级目录）。在这个文件中，你可以进行任何你想要的自定义；但是，`user-customizations.sh` **不应该被纳入版本控制（version controlled）**。

## 供应商（Provider）特定设置（Provider Specific Settings）

### VirtualBox

#### `natdnshostresolver`

默认情况下，Homestead 会将 `natdnshostresolver` 选项配置为 `on`（开启）。这使得 Homestead 可以使用宿主操作系统（host OS）的 DNS 配置。如果你希望覆盖（override）这一默认行为，请在 `Homestead.yaml` 文件中添加以下配置：

```yaml
provider: virtualbox
natdnshostresolver: 'off'
```
