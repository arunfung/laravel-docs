# Laravel Homestead

- [简介](#introduction)
- [安装与设置](#installation-and-setup)
    - [初始步骤](#first-steps)
    - [配置 Homestead](#configuring-homestead)
    - [配置 Nginx 站点](#configuring-nginx-sites)
    - [配置服务](#configuring-services)
    - [启动 Vagrant Box](#launching-the-vagrant-box)
    - [按项目安装](#per-project-installation)
    - [安装可选功能](#installing-optional-features)
    - [别名](#aliases)
- [更新 Homestead](#updating-homestead)
- [日常使用](#daily-usage)
    - [通过 SSH 连接](#connecting-via-ssh)
    - [添加更多站点](#adding-additional-sites)
    - [环境变量](#environment-variables)
    - [端口](#ports)
    - [PHP 版本](#php-versions)
    - [连接数据库](#connecting-to-databases)
    - [数据库备份](#database-backups)
    - [配置 Cron 调度](#configuring-cron-schedules)
    - [配置 Mailpit](#configuring-mailpit)
    - [配置 Minio](#configuring-minio)
    - [Laravel Dusk](#laravel-dusk)
    - [共享环境](#sharing-your-environment)
- [调试与性能分析](#debugging-and-profiling)
    - [使用 Xdebug 调试 Web 请求](#debugging-web-requests)
    - [调试 CLI 应用](#debugging-cli-applications)
    - [使用 Blackfire 分析应用性能](#profiling-applications-with-blackfire)
- [网络接口](#network-interfaces)
- [扩展 Homestead](#extending-homestead)
- [提供者专属设置](#provider-specific-settings)
    - [VirtualBox](#provider-specific-virtualbox)

<a name="introduction"></a>
## 简介

> [!WARNING]
> Laravel Homestead 是一个不再积极维护的旧扩展包，可以使用 [Laravel Sail](/docs/{{version}}/sail) 作为现代替代方案。

Laravel 致力于让整个 PHP 开发体验更加愉快，包括本地开发环境。[Laravel Homestead](https://github.com/laravel/homestead) 是官方预先打包的 Vagrant Box，提供完善的开发环境，无需在本机安装 PHP、Web 服务器或其他服务器软件。

[Vagrant](https://www.vagrantup.com) 提供了一种简单优雅的方式来管理和配置虚拟机。Vagrant Box 可以随时丢弃；如果出现问题，你可以在几分钟内销毁并重新创建它！

Homestead 可在 Windows、macOS 或 Linux 系统上运行，包含 Nginx、PHP、MySQL、PostgreSQL、Redis、Memcached、Node，以及开发出色的 Laravel 应用所需的其他软件。

> [!WARNING]
> 如果使用 Windows，可能需要启用硬件虚拟化（VT-x），通常可在 BIOS 中启用。如果在 UEFI 系统上使用 Hyper-V，可能还需要禁用 Hyper-V 才能使用 VT-x。

<a name="included-software"></a>
### 内含软件

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
- Node（包含 Yarn、Bower、Grunt 和 Gulp）
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

<a name="optional-software"></a>
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
- Trader <small>（PHP 扩展）</small>
- Webdriver 和 Laravel Dusk 工具

</div>

<a name="installation-and-setup"></a>
## 安装与设置

<a name="first-steps"></a>
### 初始步骤

启动 Homestead 环境之前，必须安装 [Vagrant](https://developer.hashicorp.com/vagrant/downloads) 以及以下受支持的提供者之一：

- [VirtualBox 6.1.x](https://www.virtualbox.org/wiki/Download_Old_Builds_6_1)
- [Parallels](https://www.parallels.com/products/desktop/)

这些软件都为主流操作系统提供易于使用的图形安装程序。

要使用 Parallels 提供者，需要安装免费的 [Parallels Vagrant 插件](https://github.com/Parallels/vagrant-parallels)。

<a name="installing-homestead"></a>
#### 安装 Homestead

你可以将 Homestead 仓库克隆到宿主机来安装 Homestead。由于 Homestead 虚拟机将作为所有 Laravel 应用的宿主机，建议将仓库克隆到主目录下的 `Homestead` 文件夹。本文将该目录称为「Homestead 目录」：

```shell
git clone https://github.com/laravel/homestead.git ~/Homestead
```

克隆 Laravel Homestead 仓库后，应检出 `release` 分支。该分支始终包含 Homestead 的最新稳定版本：

```shell
cd ~/Homestead

git checkout release
```

接下来，在 Homestead 目录中执行 `bash init.sh` 命令，创建 `Homestead.yaml` 配置文件。你可以在该文件中配置 Homestead 的所有设置；文件会放在 Homestead 目录中：

```shell
# macOS / Linux：
bash init.sh

# Windows：
init.bat
```

<a name="configuring-homestead"></a>
### 配置 Homestead

<a name="setting-your-provider"></a>
#### 设置提供者

`Homestead.yaml` 文件中的 `provider` 键指定使用哪个 Vagrant 提供者：`virtualbox` 或 `parallels`：

    provider: virtualbox

> [!WARNING]
> 如果使用 Apple Silicon，必须使用 Parallels 提供者。

<a name="configuring-shared-folders"></a>
#### 配置共享文件夹

`Homestead.yaml` 文件的 `folders` 属性列出了需要与 Homestead 环境共享的所有文件夹。当这些文件夹中的文件发生变化时，本机与 Homestead 虚拟环境之间会保持同步。你可以根据需要配置任意数量的共享文件夹：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
```

> [!WARNING]
> Windows 用户不应使用 `~/` 路径语法，而应使用项目的完整路径，例如 `C:\Users\user\Code\project1`。

应为每个应用分别配置文件夹映射，而不是映射一个包含所有应用的大目录。映射文件夹时，虚拟机必须跟踪其中*每个*文件的所有磁盘 IO。如果文件夹包含大量文件，性能可能会下降：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
    - map: ~/code/project2
      to: /home/vagrant/project2
```

> [!WARNING]
> 使用 Homestead 时，切勿挂载 `.`（当前目录）。这会导致 Vagrant 无法将当前文件夹映射到 `/vagrant`，进而破坏可选功能，并在配置过程中产生意外结果。

要启用 [NFS](https://developer.hashicorp.com/vagrant/docs/synced-folders/nfs)，可以在文件夹映射中添加 `type` 选项：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
      type: "nfs"
```

> [!WARNING]
> 在 Windows 上使用 NFS 时，建议安装 [vagrant-winnfsd](https://github.com/winnfsd/vagrant-winnfsd) 插件。该插件会为 Homestead 虚拟机中的文件和目录维持正确的用户及用户组权限。

你也可以在 `options` 键下列出 Vagrant [同步文件夹](https://developer.hashicorp.com/vagrant/docs/synced-folders/basic_usage)支持的其他选项：

```yaml
folders:
    - map: ~/code/project1
      to: /home/vagrant/project1
      type: "rsync"
      options:
          rsync__args: ["--verbose", "--archive", "--delete", "-zz"]
          rsync__exclude: ["node_modules"]
```

<a name="configuring-nginx-sites"></a>
### 配置 Nginx 站点

不熟悉 Nginx？没关系。`Homestead.yaml` 文件的 `sites` 属性可以轻松将「域名」映射到 Homestead 环境中的文件夹。该文件包含一个站点配置示例。你可以根据需要添加任意数量的站点，让 Homestead 为你开发的所有 Laravel 应用提供便利的虚拟环境：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
```

如果在配置 Homestead 虚拟机之后更改 `sites` 属性，应在终端中执行 `vagrant reload --provision` 命令，以更新虚拟机上的 Nginx 配置。

> [!WARNING]
> Homestead 脚本尽可能设计为幂等的。但如果配置过程中遇到问题，应执行 `vagrant destroy && vagrant up` 命令销毁并重建虚拟机。

<a name="hostname-resolution"></a>
#### 主机名解析

Homestead 使用 `mDNS` 发布主机名，以实现自动主机解析。如果在 `Homestead.yaml` 文件中设置 `hostname: homestead`，即可通过 `homestead.local` 访问该主机。macOS、iOS 和 Linux 桌面发行版默认支持 `mDNS`。如果使用 Windows，必须安装 [Bonjour Print Services for Windows](https://support.apple.com/kb/DL999?viewlocale=en_US&locale=en_US)。

自动主机名最适合[按项目安装](#per-project-installation)的 Homestead。如果在同一个 Homestead 实例上托管多个站点，可以将站点「域名」添加到本机的 `hosts` 文件中。该文件会将对 Homestead 站点的请求指向 Homestead 虚拟机。在 macOS 和 Linux 上，该文件位于 `/etc/hosts`；在 Windows 上，位于 `C:\Windows\System32\drivers\etc\hosts`。添加的行如下所示：

```text
192.168.56.56  homestead.test
```

确保列出的 IP 地址与 `Homestead.yaml` 文件中的设置一致。将域名添加到 `hosts` 文件并启动 Vagrant Box 后，就可以通过浏览器访问站点：

```shell
http://homestead.test
```

<a name="configuring-services"></a>
### 配置服务

Homestead 默认启动多个服务，但你可以自定义配置过程中启用或禁用的服务。例如，可以修改 `Homestead.yaml` 文件中的 `services` 选项，启用 PostgreSQL 并禁用 MySQL：

```yaml
services:
    - enabled:
        - "postgresql"
    - disabled:
        - "mysql"
```

指定的服务会按照它们在 `enabled` 和 `disabled` 指令中的顺序启动或停止。

<a name="launching-the-vagrant-box"></a>
### 启动 Vagrant Box

按需编辑 `Homestead.yaml` 后，在 Homestead 目录中运行 `vagrant up` 命令。Vagrant 会启动虚拟机，并自动配置共享文件夹和 Nginx 站点。

要销毁虚拟机，可以使用 `vagrant destroy` 命令。

<a name="per-project-installation"></a>
### 按项目安装

除了全局安装 Homestead 并让所有项目共享同一个虚拟机，也可以为每个项目配置独立的 Homestead 实例。如果希望随项目提供 `Vagrantfile`，按项目安装会很有用：其他开发者克隆项目仓库后即可立即运行 `vagrant up`。

你可以使用 Composer 包管理器将 Homestead 安装到项目中：

```shell
composer require laravel/homestead --dev
```

安装 Homestead 后，调用其 `make` 命令，为项目生成 `Vagrantfile` 和 `Homestead.yaml` 文件。这些文件会放在项目根目录中。`make` 命令还会自动配置 `Homestead.yaml` 文件中的 `sites` 和 `folders` 指令：

```shell
# macOS / Linux：
php vendor/bin/homestead make

# Windows：
vendor\\bin\\homestead make
```

接下来，在终端中运行 `vagrant up` 命令，并通过浏览器访问 `http://homestead.test`。请注意，如果没有使用自动[主机名解析](#hostname-resolution)，仍需在 `/etc/hosts` 文件中为 `homestead.test` 或你选择的域名添加一条记录。

<a name="installing-optional-features"></a>
### 安装可选功能

可通过 `Homestead.yaml` 文件中的 `features` 选项安装可选软件。大多数功能可以使用布尔值启用或禁用，也有一些功能允许配置多个选项：

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

<a name="elasticsearch"></a>
#### Elasticsearch

你可以指定受支持的 Elasticsearch 版本，必须使用精确的版本号（主版本号.次版本号.补丁号）。默认安装会创建一个名为 'homestead' 的集群。分配给 Elasticsearch 的内存不得超过操作系统内存的一半，因此应确保 Homestead 虚拟机的内存至少是 Elasticsearch 分配量的两倍。

> [!NOTE]
> 请参阅 [Elasticsearch 文档](https://www.elastic.co/guide/en/elasticsearch/reference/current)，了解如何自定义配置。

<a name="mariadb"></a>
#### MariaDB

启用 MariaDB 会移除 MySQL 并安装 MariaDB。应用应使用 `mariadb` 数据库驱动，而非 `mysql`：两者都能连接，但只有 `mariadb` 驱动会生成 MariaDB 专用的 SQL，例如向量距离查询。

<a name="mongodb"></a>
#### MongoDB

默认安装的 MongoDB 会将数据库用户名设为 `homestead`，对应密码设为 `secret`。

<a name="neo4j"></a>
#### Neo4j

默认安装的 Neo4j 会将数据库用户名设为 `homestead`，对应密码设为 `secret`。要访问 Neo4j 浏览器，请在浏览器中访问 `http://homestead.test:7474`。端口 `7687`（Bolt）、`7474`（HTTP）和 `7473`（HTTPS）可用于处理 Neo4j 客户端的请求。

<a name="aliases"></a>
### 别名

你可以修改 Homestead 目录中的 `aliases` 文件，为 Homestead 虚拟机添加 Bash 别名：

```shell
alias c='clear'
alias ..='cd ..'
```

更新 `aliases` 文件后，应使用 `vagrant reload --provision` 命令重新配置 Homestead 虚拟机，确保新别名在虚拟机上可用。

<a name="updating-homestead"></a>
## 更新 Homestead

开始更新 Homestead 之前，应在 Homestead 目录中运行以下命令，确保已移除当前虚拟机：

```shell
vagrant destroy
```

接下来，需要更新 Homestead 源代码。如果你克隆了仓库，可以在原先克隆仓库的位置执行以下命令：

```shell
git fetch

git pull origin release
```

这些命令会从 GitHub 仓库拉取最新的 Homestead 代码、获取最新标签，然后检出最新的标签版本。你可以在 Homestead 的 [GitHub 发布页面](https://github.com/laravel/homestead/releases)找到最新稳定版本。

如果通过项目的 `composer.json` 文件安装了 Homestead，应确保该文件包含 `"laravel/homestead": "^12"`，然后更新依赖：

```shell
composer update
```

接下来，使用 `vagrant box update` 命令更新 Vagrant Box：

```shell
vagrant box update
```

更新 Vagrant Box 后，应在 Homestead 目录中运行 `bash init.sh` 命令，更新 Homestead 的其他配置文件。系统会询问是否覆盖已有的 `Homestead.yaml`、`after.sh` 和 `aliases` 文件：

```shell
# macOS / Linux：
bash init.sh

# Windows：
init.bat
```

最后，需要重新生成 Homestead 虚拟机，以使用最新的 Vagrant 安装：

```shell
vagrant up
```

<a name="daily-usage"></a>
## 日常使用

<a name="connecting-via-ssh"></a>
### 通过 SSH 连接

你可以在 Homestead 目录中执行 `vagrant ssh` 终端命令，通过 SSH 连接到虚拟机。

<a name="adding-additional-sites"></a>
### 添加更多站点

Homestead 环境配置完成并运行后，你可能希望为其他 Laravel 项目添加 Nginx 站点。单个 Homestead 环境可以运行任意数量的 Laravel 项目。要添加站点，请将其添加到 `Homestead.yaml` 文件中。

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
    - map: another.test
      to: /home/vagrant/project2/public
```

> [!WARNING]
> 添加站点之前，应确保已为项目目录配置[文件夹映射](#configuring-shared-folders)。

如果 Vagrant 没有自动管理 `hosts` 文件，你可能还需要将新站点添加到该文件中。在 macOS 和 Linux 上，该文件位于 `/etc/hosts`；在 Windows 上，位于 `C:\Windows\System32\drivers\etc\hosts`：

```text
192.168.56.56  homestead.test
192.168.56.56  another.test
```

添加站点后，在 Homestead 目录中执行 `vagrant reload --provision` 终端命令。

<a name="site-types"></a>
#### 站点类型

Homestead 支持多种站点「类型」，方便你运行不基于 Laravel 的项目。例如，可以使用 `statamic` 站点类型轻松地将 Statamic 应用添加到 Homestead：

```yaml
sites:
    - map: statamic.test
      to: /home/vagrant/my-symfony-project/web
      type: "statamic"
```

可用的站点类型包括：`apache`、`apache-proxy`、`apigility`、`expressive`、`laravel`（默认）、`proxy`（用于 nginx）、`silverstripe`、`statamic`、`symfony2`、`symfony4` 和 `zf`。

<a name="site-parameters"></a>
#### 站点参数

你可以通过站点的 `params` 指令，为站点添加额外的 Nginx `fastcgi_param` 值：

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

你可以通过在 `Homestead.yaml` 文件中添加变量来定义全局环境变量：

```yaml
variables:
    - key: APP_ENV
      value: local
    - key: FOO
      value: bar
```

更新 `Homestead.yaml` 文件后，请务必执行 `vagrant reload --provision` 命令重新配置虚拟机。这将更新所有已安装 PHP 版本的 PHP-FPM 配置，也会更新 `vagrant` 用户的环境。

<a name="ports"></a>
### 端口

默认情况下，以下端口会转发到 Homestead 环境：

<div class="content-list" markdown="1">

- **HTTP：** 8000 &rarr; 转发到 80
- **HTTPS：** 44300 &rarr; 转发到 443

</div>

<a name="forwarding-additional-ports"></a>
#### 转发其他端口

如果需要，可以在 `Homestead.yaml` 文件中定义 `ports` 配置项，将其他端口转发到 Vagrant Box。更新文件后，请务必执行 `vagrant reload --provision` 命令重新配置虚拟机：

```yaml
ports:
    - send: 50000
      to: 5000
    - send: 7777
      to: 777
      protocol: udp
```

下面列出了你可能希望从宿主机映射到 Vagrant Box 的其他 Homestead 服务端口：

<div class="content-list" markdown="1">

- **SSH：** 2222 &rarr; 目标端口 22
- **ngrok UI：** 4040 &rarr; 目标端口 4040
- **MySQL：** 33060 &rarr; 目标端口 3306
- **PostgreSQL：** 54320 &rarr; 目标端口 5432
- **MongoDB：** 27017 &rarr; 目标端口 27017
- **Mailpit：** 8025 &rarr; 目标端口 8025
- **Minio：** 9600 &rarr; 目标端口 9600

</div>

<a name="php-versions"></a>
### PHP 版本

Homestead 支持在同一台虚拟机上运行多个 PHP 版本。你可以在 `Homestead.yaml` 文件中为站点指定使用的 PHP 版本。可用版本包括「5.6」、「7.0」、「7.1」、「7.2」、「7.3」、「7.4」、「8.0」、「8.1」、「8.2」和默认的「8.3」：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
      php: "7.1"
```

[在 Homestead 虚拟机中](#connecting-via-ssh)，你可以通过 CLI 使用任何受支持的 PHP 版本：

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

你可以在 Homestead 虚拟机中执行以下命令，切换 CLI 默认使用的 PHP 版本：

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

MySQL 和 PostgreSQL 默认都配置了一个 `homestead` 数据库。要从宿主机的数据库客户端连接，请连接到 `127.0.0.1` 的 `33060`（MySQL）或 `54320`（PostgreSQL）端口。两个数据库的用户名和密码均为 `homestead` / `secret`。

> [!WARNING]
> 只有从宿主机连接数据库时才应使用这些非标准端口。由于 Laravel 运行在虚拟机_内部_，应用的 `database` 配置文件应使用默认的 3306 和 5432 端口。

<a name="database-backups"></a>
### 数据库备份

销毁 Homestead 虚拟机时，Homestead 可以自动备份数据库。使用此功能需要 Vagrant 2.1.0 或更高版本；如果使用较旧版本，则必须安装 `vagrant-triggers` 插件。要启用自动数据库备份，请在 `Homestead.yaml` 文件中添加以下行：

```yaml
backup: true
```

完成配置后，执行 `vagrant destroy` 命令时，Homestead 会将数据库导出到 `.backup/mysql_backup` 和 `.backup/postgres_backup` 目录。这些目录位于 Homestead 的安装目录中；如果使用[按项目安装](#per-project-installation)，则位于项目根目录中。

<a name="configuring-cron-schedules"></a>
### 配置 Cron 调度

Laravel 提供了一种方便的[调度 Cron 任务](/docs/{{version}}/scheduling)方式：只需安排 `schedule:run` Artisan 命令每分钟运行一次。该命令会检查 `routes/console.php` 文件中定义的任务计划，确定需要运行哪些计划任务。

如果希望为 Homestead 站点运行 `schedule:run` 命令，可以在定义站点时将 `schedule` 选项设为 `true`：

```yaml
sites:
    - map: homestead.test
      to: /home/vagrant/project1/public
      schedule: true
```

站点的 Cron 任务会定义在 Homestead 虚拟机的 `/etc/cron.d` 目录中。

<a name="configuring-mailpit"></a>
### 配置 Mailpit

[Mailpit](https://github.com/axllent/mailpit) 允许你拦截并检查外发邮件，而无需将邮件实际发送给收件人。首先，更新应用的 `.env` 文件，使用以下邮件设置：

```ini
MAIL_MAILER=smtp
MAIL_HOST=localhost
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
```

配置 Mailpit 后，可以通过 `http://localhost:8025` 访问其控制面板。

<a name="configuring-minio"></a>
### 配置 Minio

[Minio](https://github.com/minio/minio) 是一个开源对象存储服务器，提供兼容 Amazon S3 的 API。要安装 Minio，请在 `Homestead.yaml` 文件的 [features](#installing-optional-features) 部分添加以下配置选项：

    minio: true

默认情况下，Minio 使用 9600 端口。可以通过 `http://localhost:9600` 访问 Minio 控制面板。默认访问密钥为 `homestead`，默认私密密钥为 `secretkey`。访问 Minio 时，应始终使用 `us-east-1` 区域。

要使用 Minio，请确保 `.env` 文件包含以下选项：

```ini
AWS_USE_PATH_STYLE_ENDPOINT=true
AWS_ENDPOINT=http://localhost:9600
AWS_ACCESS_KEY_ID=homestead
AWS_SECRET_ACCESS_KEY=secretkey
AWS_DEFAULT_REGION=us-east-1
```

要配置由 Minio 提供的「S3」存储桶，请在 `Homestead.yaml` 文件中添加 `buckets` 指令。定义存储桶后，应在终端中执行 `vagrant reload --provision` 命令：

```yaml
buckets:
    - name: your-bucket
      policy: public
    - name: your-private-bucket
      policy: none
```

支持的 `policy` 值包括 `none`、`download`、`upload` 和 `public`。

<a name="laravel-dusk"></a>
### Laravel Dusk

要在 Homestead 中运行 [Laravel Dusk](/docs/{{version}}/dusk) 测试，应在 Homestead 配置中启用 [webdriver 功能](#installing-optional-features)：

```yaml
features:
    - webdriver: true
```

启用 `webdriver` 功能后，应在终端中执行 `vagrant reload --provision` 命令。

<a name="sharing-your-environment"></a>
### 共享环境

有时你可能希望与同事或客户分享正在开发的内容。Vagrant 内置了 `vagrant share` 命令来支持这一功能，但如果 `Homestead.yaml` 文件中配置了多个站点，该命令将无法使用。

为解决这一问题，Homestead 提供了自己的 `share` 命令。首先，通过 `vagrant ssh` [使用 SSH 连接到 Homestead 虚拟机](#connecting-via-ssh)，然后执行 `share homestead.test` 命令。该命令会共享 `Homestead.yaml` 配置文件中的 `homestead.test` 站点。你也可以将 `homestead.test` 替换为其他已配置的站点：

```shell
share homestead.test
```

运行命令后，将出现 Ngrok 界面，其中包含活动日志和共享站点的公开访问 URL。如果需要指定自定义区域、子域名或其他 Ngrok 运行时选项，可以将它们添加到 `share` 命令中：

```shell
share homestead.test -region=eu -subdomain=laravel
```

如果需要通过 HTTPS 而非 HTTP 共享内容，可以使用 `sshare` 命令代替 `share`。

> [!WARNING]
> 请注意，Vagrant 本身并不安全；运行 `share` 命令时，你会将虚拟机暴露到互联网。

<a name="debugging-and-profiling"></a>
## 调试与性能分析

<a name="debugging-web-requests"></a>
### 使用 Xdebug 调试 Web 请求

Homestead 支持使用 [Xdebug](https://xdebug.org) 进行单步调试。例如，你可以在浏览器中访问页面，PHP 会连接到 IDE，让你检查和修改运行中的代码。

默认情况下，Xdebug 已运行并准备好接受连接。如果需要在 CLI 中启用 Xdebug，请在 Homestead 虚拟机中执行 `sudo phpenmod xdebug` 命令。接下来，按照 IDE 的说明启用调试。最后，配置浏览器通过扩展或[书签脚本](https://www.jetbrains.com/phpstorm/marklets/)触发 Xdebug。

> [!WARNING]
> Xdebug 会显著降低 PHP 的运行速度。要禁用 Xdebug，请在 Homestead 虚拟机中运行 `sudo phpdismod xdebug` 并重启 FPM 服务。

<a name="autostarting-xdebug"></a>
#### 自动启动 Xdebug

调试向 Web 服务器发送请求的功能测试时，自动启动调试通常比修改测试、通过自定义请求头或 Cookie 触发调试更方便。要强制 Xdebug 自动启动，请修改 Homestead 虚拟机中的 `/etc/php/7.x/fpm/conf.d/20-xdebug.ini` 文件，并添加以下配置：

```ini
; 如果 Homestead.yaml 中 IP 地址使用不同的子网，此地址可能不同……
xdebug.client_host = 192.168.10.1
xdebug.mode = debug
xdebug.start_with_request = yes
```

<a name="debugging-cli-applications"></a>
### 调试 CLI 应用

要调试 PHP CLI 应用，请在 Homestead 虚拟机中使用 `xphp` shell 别名：

```shell
xphp /path/to/script
```

<a name="profiling-applications-with-blackfire"></a>
### 使用 Blackfire 分析应用性能

[Blackfire](https://blackfire.io/docs/introduction) 是一项用于分析 Web 请求和 CLI 应用性能的服务。它提供交互式用户界面，以调用图和时间线显示分析数据。它适用于开发、预发布和生产环境，且不会给最终用户带来额外开销。此外，Blackfire 还会检查代码和 `php.ini` 配置的性能、质量与安全性。

开源应用 [Blackfire Player](https://blackfire.io/docs/player/index) 提供网页爬取、Web 测试和数据抓取功能，可以与 Blackfire 配合使用，通过脚本编写性能分析场景。

要启用 Blackfire，请使用 Homestead 配置文件中的 `features` 设置：

```yaml
features:
    - blackfire:
        server_id: "server_id"
        server_token: "server_value"
        client_id: "client_id"
        client_token: "client_value"
```

Blackfire 服务器凭证和客户端凭证[需要 Blackfire 账户](https://blackfire.io/signup)。Blackfire 提供多种分析应用性能的方式，包括 CLI 工具和浏览器扩展。详情请[参阅 Blackfire 文档](https://blackfire.io/docs/php/integrations/laravel/index)。

<a name="network-interfaces"></a>
## 网络接口

`Homestead.yaml` 文件的 `networks` 属性用于配置 Homestead 虚拟机的网络接口。你可以根据需要配置任意数量的接口：

```yaml
networks:
    - type: "private_network"
      ip: "192.168.10.20"
```

要启用[桥接](https://developer.hashicorp.com/vagrant/docs/networking/public_network)接口，请为网络配置 `bridge` 设置，并将网络类型改为 `public_network`：

```yaml
networks:
    - type: "public_network"
      ip: "192.168.10.20"
      bridge: "en1: Wi-Fi (AirPort)"
```

要启用 [DHCP](https://developer.hashicorp.com/vagrant/docs/networking/public_network#dhcp)，只需从配置中移除 `ip` 选项：

```yaml
networks:
    - type: "public_network"
      bridge: "en1: Wi-Fi (AirPort)"
```

要更改网络使用的设备，可以在网络配置中添加 `dev` 选项。`dev` 的默认值为 `eth0`：

```yaml
networks:
    - type: "public_network"
      ip: "192.168.10.20"
      bridge: "en1: Wi-Fi (AirPort)"
      dev: "enp2s0"
```

<a name="extending-homestead"></a>
## 扩展 Homestead

你可以使用 Homestead 目录根部的 `after.sh` 脚本扩展 Homestead。在该文件中，可以添加正确配置和自定义虚拟机所需的 shell 命令。

自定义 Homestead 时，Ubuntu 可能会询问你要保留软件包的原始配置，还是用新配置文件覆盖它。为避免这一提示及覆盖 Homestead 先前写入的配置，应在安装软件包时使用以下命令：

```shell
sudo apt-get -y \
    -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" \
    install package-name
```

<a name="user-customizations"></a>
### 用户自定义

与团队一起使用 Homestead 时，你可能希望调整 Homestead 以更好地适应自己的开发习惯。为此，可以在 Homestead 目录根部（即包含 `Homestead.yaml` 的目录）创建 `user-customizations.sh` 文件，在其中进行所需的自定义。但不应将该文件纳入版本控制。

<a name="provider-specific-settings"></a>
## 提供者专属设置

<a name="provider-specific-virtualbox"></a>
### VirtualBox

<a name="natdnshostresolver"></a>
#### `natdnshostresolver`

默认情况下，Homestead 将 `natdnshostresolver` 设置为 `on`，使其能够使用宿主操作系统的 DNS 设置。如果希望覆盖这一行为，请在 `Homestead.yaml` 文件中添加以下配置选项：

```yaml
provider: virtualbox
natdnshostresolver: 'off'
```
