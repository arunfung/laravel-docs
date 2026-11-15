
# Laravel Scout

-   [简介](#introduction)
-   [安装](#installation)
    -   [队列](#queueing)
-   [驱动先决条件](#driver-prerequisites)
    -   [Algolia](#algolia)
    -   [Meilisearch](#meilisearch)
    -   [Typesense](#typesense)
-   [配置](#configuration)
    -   [配置模型索引](#configuring-model-indexes)
    -   [配置可搜索数据](#configuring-searchable-data)
    -   [配置模型 ID](#configuring-the-model-id)
    -   [为模型配置搜索引擎](#configuring-search-engines-per-model)
    -   [识别用户](#identifying-users)
-   [数据库 / 集合引擎](#database-and-collection-engines)
    -   [数据库引擎](#database-engine)
    -   [集合引擎](#collection-engine)
-   [索引](#indexing)
    -   [批量导入](#batch-import)
    -   [添加记录](#adding-records)
    -   [更新记录](#updating-records)
    -   [删除记录](#removing-records)
    -   [暂停索引](#pausing-indexing)
    -   [有条件的可搜索模型实例](#conditionally-searchable-model-instances)
-   [搜索](#searching)
    -   [Where 子句](#where-clauses)
    -   [分页](#pagination)
    -   [软删除](#soft-deleting)
    -   [自定义引擎搜索](#customizing-engine-searches)
-   [自定义引擎](#custom-engines)

## 简介

[Laravel Scout](https://github.com/laravel/scout?utm_source=chatgpt.com) 提供了一种基于驱动的简单解决方案，用于给你的 [Eloquent 模型](/docs/laravel/12.x/eloquent) 添加全文搜索功能。Scout 使用模型观察器，会自动保持你的搜索索引与 Eloquent 记录同步。

目前，Scout 自带了 [Algolia](https://www.algolia.com/?utm_source=chatgpt.com)、[Meilisearch](https://www.meilisearch.com?utm_source=chatgpt.com)、[Typesense](https://typesense.org?utm_source=chatgpt.com)，以及 MySQL / PostgreSQL (`database`) 驱动。除此之外，Scout 还包含一个专为本地开发使用设计的 “collection” 驱动，它不需要任何外部依赖或第三方服务。并且，编写自定义驱动也很简单，你可以自由扩展 Scout 来实现自己的搜索功能。

## 安装

首先，通过 Composer 包管理器安装 Scout：

```shell
composer require laravel/scout
```

安装完成后，你应该使用 `vendor:publish` Artisan 命令发布 Scout 的配置文件。该命令会将 `scout.php` 配置文件发布到应用的 `config` 目录中：

```shell
php artisan vendor:publish --provider="Laravel\Scout\ScoutServiceProvider"
```



最后，把 `Laravel\Scout\Searchable` trait 添加到你想要设置为可搜索的模型中。这个 trait 会注册一个模型观察器，它会自动保持模型与搜索驱动同步：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Post extends Model
{
    use Searchable;
}
```

### 队列

虽然使用 Scout 并不严格要求，但在使用该库之前，你应该强烈考虑配置一个 [队列驱动](/docs/laravel/12.x/queues)。运行队列工作器将允许 Scout 将所有同步模型信息到搜索索引的操作加入队列，从而为你的应用 Web 界面提供更好的响应时间。

一旦你配置好了队列驱动，请将 `config/scout.php` 配置文件中的 `queue` 选项值设置为 `true`：

```php
'queue' => true,
```

即使当 `queue` 选项设置为 `false` 时，也要记住某些 Scout 驱动（如 Algolia 和 Meilisearch）始终是异步索引记录的。也就是说，即便索引操作在 Laravel 应用中已完成，搜索引擎本身可能不会立即反映新的或更新的记录。

要指定 Scout 作业所使用的连接和队列，可以将 `queue` 配置项定义为一个数组：

```php
'queue' => [
    'connection' => 'redis',
    'queue' => 'scout'
],
```

当然，如果你自定义了 Scout 作业所使用的连接和队列，你应该运行一个队列工作器来处理该连接和队列上的作业：

```shell
php artisan queue:work redis --queue=scout
```


## 驱动先决条件

### Algolia

当使用 Algolia 驱动时，你需要在 `config/scout.php` 配置文件中配置 Algolia 的 `id` 和 `secret` 凭证。配置好凭证后，你还需要通过 Composer 包管理器安装 Algolia PHP SDK：

```shell
composer require algolia/algoliasearch-client-php
```

### Meilisearch

[Meilisearch](https://www.meilisearch.com?utm_source=chatgpt.com) 是一个极速且开源的搜索引擎。如果你不确定如何在本地计算机上安装 Meilisearch，可以使用 [Laravel Sail](/docs/laravel/12.x/sail#meilisearch)，这是 Laravel 官方支持的 Docker 开发环境。

当使用 Meilisearch 驱动时，你需要通过 Composer 包管理器安装 Meilisearch PHP SDK：

```shell
composer require meilisearch/meilisearch-php http-interop/http-factory-guzzle
```

然后，在应用的 `.env` 文件中设置 `SCOUT_DRIVER` 环境变量，以及 Meilisearch 的 `host` 和 `key` 凭证：

```ini
SCOUT_DRIVER=meilisearch
MEILISEARCH_HOST=http://127.0.0.1:7700
MEILISEARCH_KEY=masterKey
```

关于 Meilisearch 的更多信息，请查阅 [Meilisearch 文档](https://docs.meilisearch.com/learn/getting_started/quick_start.html?utm_source=chatgpt.com)。

此外，你应该确保安装的 `meilisearch/meilisearch-php` 版本与所使用的 Meilisearch 二进制版本兼容，可以参考 [Meilisearch 关于二进制兼容性的文档](https://github.com/meilisearch/meilisearch-php?utm_source=chatgpt.com#-compatibility-with-meilisearch)。

> [!警告]
> 当在一个使用 Meilisearch 的应用中升级 Scout 时，你应当始终 [检查 Meilisearch 服务本身的额外重大变更](https://github.com/meilisearch/Meilisearch/releases?utm_source=chatgpt.com)。

### Typesense

[Typesense](https://typesense.org?utm_source=chatgpt.com) 是一个极速、开源的搜索引擎，支持关键词搜索、语义搜索、地理搜索以及向量搜索。


你可以选择 [自托管](https://typesense.org/docs/guide/install-typesense.html?utm_source=chatgpt.com#option-2-local-machine-self-hosting) Typesense，或者使用 [Typesense Cloud](https://cloud.typesense.org?utm_source=chatgpt.com)。

要在 Scout 中开始使用 Typesense，请通过 Composer 包管理器安装 Typesense PHP SDK：

```shell
composer require typesense/typesense-php
```

然后，在应用的 `.env` 文件中设置 `SCOUT_DRIVER` 环境变量，以及 Typesense 的主机和 API key 凭证：

```ini
SCOUT_DRIVER=typesense
TYPESENSE_API_KEY=masterKey
TYPESENSE_HOST=localhost
```

如果你正在使用 [Laravel Sail](/docs/laravel/12.x/sail)，你可能需要调整 `TYPESENSE_HOST` 环境变量以匹配 Docker 容器的名称。你也可以选择性地指定安装的端口、路径和协议：

```ini
TYPESENSE_PORT=8108
TYPESENSE_PATH=
TYPESENSE_PROTOCOL=http
```

关于 Typesense 集合的额外设置和 schema 定义，可以在应用的 `config/scout.php` 配置文件中找到。更多关于 Typesense 的信息，请参考 [Typesense 文档](https://typesense.org/docs/guide/?utm_source=chatgpt.com#quick-start)。

#### 为存储到 Typesense 做数据准备

在使用 Typesense 时，你的可搜索模型必须定义一个 `toSearchableArray` 方法，将模型的主键转换为字符串，并将创建日期转换为 UNIX 时间戳：

```php
/**
 * 获取该模型的可索引数据数组
 *
 * @return array<string, mixed>
 */
public function toSearchableArray(): array
{
    return array_merge($this->toArray(),[
        'id' => (string) $this->id,
        'created_at' => $this->created_at->timestamp,
    ]);
}
```

你还应该在应用的 `config/scout.php` 文件中定义 Typesense 集合的 schema。集合 schema 描述了每个可通过 Typesense 搜索的字段的数据类型。有关所有可用 schema 选项的更多信息，请参考 [Typesense 文档](https://typesense.org/docs/latest/api/collections.html?utm_source=chatgpt.com#schema-parameters)。



如果你需要在定义 Typesense 集合架构之后进行修改，你可以选择以下两种方式之一：
 执行 `scout:flush` 与 `scout:import`这将**删除所有已存在的索引数据**并重新建立架构。  或者可以使用 Typesense 的 API 修改集合的架构，而**不会删除任何已索引的数据**。
 
如果你的可搜索模型支持「软删除」，你应该在应用程序的 config/scout.php 配置文件中，为模型对应的 Typesense 架构定义一个 __soft_deleted 字段:

```php
User::class => [
    'collection-schema' => [
        'fields' => [
            // ...
            [
                'name' => '__soft_deleted',
                'type' => 'int32',
                'optional' => true,
            ],
        ],
    ],
],
```

<a name="typesense-dynamic-search-parameters"></a>
#### 动态搜索参数

Typesense 允许你在通过 `options` 方法执行搜索操作时，**动态修改**你的 [搜索参数](https://typesense.org/docs/latest/api/search.html#search-parameters) :


```php
use App\Models\Todo;

Todo::search('Groceries')->options([
    'query_by' => 'title, description'
])->get();
```

<a name="configuration"></a>
## 配置

<a name="configuring-model-indexes"></a>
### 配置模型索引

每个 Eloquent 模型都会同步到一个指定的搜索「索引」，该索引包含该模型的所有可搜索记录。你也可以把每个索引理解为一个类似 MySQL 表的结构。  默认情况下，每个模型会持久化到与模型常规「表名」对应的索引中。通常这个名称是模型名称的复数形式。  
但是，你也可以通过在模型中重写 `searchableAs` 方法来自定义模型的索引:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Post extends Model
{
    use Searchable;

    /**
     * 获取与模型关联的索引名称.
     */
    public function searchableAs(): string
    {
        return 'posts_index';
    }
}
```



<a name="configuring-searchable-data"></a>
### 配置可搜索数据

默认情况下，模型的整个 toArray 结果会被保存到搜索索引中。
如果你想自定义哪些数据需要同步到搜索索引，可以在模型中重写 toSearchableArray 方法:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Post extends Model
{
    use Searchable;

    /**
     * 获取模型的可索引数据数组.
     *
     * @return array<string, mixed>
     */
    public function toSearchableArray(): array
    {
        $array = $this->toArray();

        // 自定义数据数组...

        return $array;
    }
}
```

一些搜索引擎（例如 Meilisearch）在执行过滤操作时（比如 >、< 等比较），只会对数据类型正确的字段有效。
所以，当你在使用这些搜索引擎并自定义可搜索数据时，必须确保数值字段被转换成真正的数字类型，而不是字符串，否则过滤和比较可能无法正常工作:

```php
public function toSearchableArray()
{
    return [
        'id' => (int) $this->id,
        'name' => $this->name,
        'price' => (float) $this->price,
    ];
}
```

<a name="configuring-indexes-for-algolia"></a>
#### 配置索引设置 (Algolia)

有时候，你可能希望为 Algolia 索引 配置一些额外的设置。你可以通过 Algolia 的 UI 来管理这些设置，也可以直接在应用的 config/scout.php 配置文件中管理索引配置状态会更高效。这种方式的优点，可以通过应用的自动化部署流程发布这些设置,避免手动配置,保证多个环境中的设置保持一致。
在配置中设置 可过滤属性（filterable attributes）、排序规则（ranking）、分面（faceting），或者其他 [Algolia ](https://www.algolia.com/doc/rest-api/search/#tag/Indices/operation/setSettings) 支持的设置。
要开始使用，只需在应用的 config/scout.php 文件中，为每个索引添加对应的设置即可:

```php
use App\Models\User;
use App\Models\Flight;

'algolia' => [
    'id' => env('ALGOLIA_APP_ID', ''),
    'secret' => env('ALGOLIA_SECRET', ''),
    'index-settings' => [
        User::class => [
            'searchableAttributes' => ['id', 'name', 'email'],
            'attributesForFaceting'=> ['filterOnly(email)'],
            // 其他设置字段...
        ],
        Flight::class => [
            'searchableAttributes'=> ['id', 'destination'],
        ],
    ],
],
```



如果某个索引对应的模型支持软删除（soft deletable），并且包含在 `index-settings` 数组中，Scout 会自动在该索引上支持对软删除模型进行分面（faceting）。如果你不需要为软删除模型索引定义其他分面属性，你可以在 `index-settings` 数组中为该模型添加一个空条目：

```php
'index-settings' => [
    Flight::class => []
],
```

在配置好应用程序的索引设置后，你必须运行 `scout:sync-index-settings` Artisan 命令。此命令会将你当前配置的索引设置通知给 Algolia。为了方便，你可以将该命令加入到部署流程中：

```shell
php artisan scout:sync-index-settings
```

#### 配置可过滤数据和索引设置（Meilisearch）

与 Scout 的其他驱动不同，Meilisearch 需要你预先定义索引的搜索设置，例如可过滤属性（filterable attributes）、可排序属性（sortable attributes）以及[其他支持的设置字段](https://docs.meilisearch.com/reference/api/settings.html)。

可过滤属性指的是你计划在调用 Scout 的 `where` 方法时进行过滤的属性，而可排序属性指的是你计划在调用 `orderBy` 方法时进行排序的属性。要定义索引设置，请调整应用程序 `scout` 配置文件中 `meilisearch` 配置条目中的 `index-settings` 部分：

```php
use App\Models\User;
use App\Models\Flight;

'meilisearch' => [
    'host' => env('MEILISEARCH_HOST', 'http://localhost:7700'),
    'key' => env('MEILISEARCH_KEY', null),
    'index-settings' => [
        User::class => [
            'filterableAttributes'=> ['id', 'name', 'email'],
            'sortableAttributes' => ['created_at'],
            // Other settings fields...
        ],
        Flight::class => [
            'filterableAttributes'=> ['id', 'destination'],
            'sortableAttributes' => ['updated_at'],
        ],
    ],
],
```

如果某个索引对应的模型支持软删除，并且包含在 `index-settings` 数组中，Scout 会自动在该索引上支持对软删除模型进行过滤。如果你不需要为软删除模型索引定义其他可过滤或可排序属性，你可以在 `index-settings` 数组中为该模型添加一个空条目：

```php
'index-settings' => [
    Flight::class => []
],
```

在配置好应用程序的索引设置后，你必须运行 `scout:sync-index-settings` Artisan 命令。此命令会将你当前配置的索引设置通知给 Meilisearch。为了方便，你可以将该命令加入到部署流程中：

```shell
php artisan scout:sync-index-settings
```



### 配置模型 ID

默认情况下，Scout 会使用模型的主键作为存储在搜索索引中的模型唯一 ID/键。如果你需要自定义此行为，可以在模型中重写 `getScoutKey` 和 `getScoutKeyName` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class User extends Model
{
    use Searchable;

    /**
     * 获取用于索引模型的值。
     */
    public function getScoutKey(): mixed
    {
        return $this->email;
    }

    /**
     * 获取用于索引模型的键名。
     */
    public function getScoutKeyName(): mixed
    {
        return 'email';
    }
}
```

### 为每个模型配置搜索引擎

在搜索时，Scout 通常会使用应用程序 `scout` 配置文件中指定的默认搜索引擎。但是，你可以通过在模型中重写 `searchableUsing` 方法，为特定模型更改搜索引擎：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Engines\Engine;
use Laravel\Scout\EngineManager;
use Laravel\Scout\Searchable;

class User extends Model
{
    use Searchable;

    /**
     * 获取用于索引模型的搜索引擎。
     */
    public function searchableUsing(): Engine
    {
        return app(EngineManager::class)->engine('meilisearch');
    }
}
```

### 用户识别

Scout 还允许你在使用 [Algolia](https://algolia.com) 时自动识别用户。将已认证的用户与搜索操作关联起来，有助于在 Algolia 仪表盘中查看搜索分析。你可以在应用程序的 `.env` 文件中通过定义 `SCOUT_IDENTIFY` 环境变量为 `true` 来启用用户识别：

```ini
SCOUT_IDENTIFY=true
```



启用此功能还会将请求的 IP 地址以及已认证用户的主标识符传递给 Algolia，这样这些数据就会与用户发起的任何搜索请求相关联。

## 数据库 / 集合引擎

### 数据库引擎

> [!警告]
> 数据库引擎目前支持 MySQL 和 PostgreSQL。

如果你的应用程序与小型到中型数据库交互，或者工作负载较轻，你可能会发现使用 Scout 的“数据库”引擎更方便入手。数据库引擎会在从现有数据库中过滤结果时使用“where like”子句和全文索引，以确定与你的查询匹配的搜索结果。

要使用数据库引擎，你只需将 `SCOUT_DRIVER` 环境变量的值设置为 `database`，或者在应用程序的 `scout` 配置文件中直接指定 `database` 驱动：

```ini
SCOUT_DRIVER=database
```

一旦你指定数据库引擎作为首选驱动，你必须 [配置可搜索数据](#configuring-searchable-data)。然后，你就可以开始针对你的模型 [执行搜索查询](#searching) 了。使用数据库引擎时，不需要执行搜索引擎索引操作，例如为 Algolia、Meilisearch 或 Typesense 索引生成数据的索引操作。

#### 自定义数据库搜索策略

默认情况下，数据库引擎会对你已 [配置为可搜索](#configuring-searchable-data) 的每个模型属性执行“where like”查询。然而，在某些情况下，这可能会导致性能较差。因此，数据库引擎的搜索策略可以配置，使得某些指定列使用全文搜索查询，或者只使用“where like”约束来搜索字符串前缀（`example%`），而不是在整个字符串中搜索（`%example%`）。



要定义此行为，你可以将 PHP 属性分配给模型的 `toSearchableArray` 方法。任何未被分配额外搜索策略行为的列，将继续使用默认的“where like”策略：

```php
use Laravel\Scout\Attributes\SearchUsingFullText;
use Laravel\Scout\Attributes\SearchUsingPrefix;

/**
 * 获取模型可索引的数据数组。
 *
 * @return array<string, mixed>
 */
#[SearchUsingPrefix(['id', 'email'])]
#[SearchUsingFullText(['bio'])]
public function toSearchableArray(): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        'bio' => $this->bio,
    ];
}
```

> [!警告]
> 在指定某列使用全文查询约束之前，请确保该列已经被分配了 [全文索引](/docs/laravel/12.x/migrations#available-index-types)。

### 集合引擎（Collection Engine）

在本地开发时，你可以自由使用 Algolia、Meilisearch 或 Typesense 搜索引擎，但你可能会发现使用“集合”引擎更方便入手。集合引擎会对现有数据库的结果使用“where”子句和集合过滤，以确定与你的查询匹配的搜索结果。使用此引擎时，不需要对可搜索模型进行“索引”，它们将直接从本地数据库中获取。

要使用集合引擎，你只需将 `SCOUT_DRIVER` 环境变量的值设置为 `collection`，或者在应用程序的 `scout` 配置文件中直接指定 `collection` 驱动：

```ini
SCOUT_DRIVER=collection
```

一旦你指定集合驱动作为首选驱动，你就可以开始针对你的模型 [执行搜索查询](#searching)。使用集合引擎时，不需要执行搜索引擎索引操作，例如为 Algolia、Meilisearch 或 Typesense 索引生成数据的索引操作。



#### 与数据库引擎的区别

乍一看，“数据库（database）”引擎和“集合（collections）”引擎非常相似。它们都直接与数据库交互以获取搜索结果。然而，集合引擎并不使用全文索引或 `LIKE` 子句来查找匹配的记录。相反，它会拉取所有可能的记录，并使用 Laravel 的 `Str::is` 辅助方法来判断搜索字符串是否存在于模型属性值中。

集合引擎是最可移植的搜索引擎，因为它适用于 Laravel 支持的所有关系型数据库（包括 SQLite 和 SQL Server）；但是，它的效率比 Scout 的数据库引擎低。

## 索引（Indexing）

### 批量导入（Batch Import）

如果你在现有项目中安装 Scout，你可能已经有一些数据库记录需要导入到索引中。Scout 提供了一个 `scout:import` Artisan 命令，可以将你所有现有记录导入到搜索索引中：

```shell
php artisan scout:import "App\Models\Post"
```

你可以使用 `flush` 命令从搜索索引中移除某个模型的所有记录：

```shell
php artisan scout:flush "App\Models\Post"
```

#### 修改导入查询

如果你想修改用于检索所有模型以进行批量导入的查询，可以在模型中定义 `makeAllSearchableUsing` 方法。在这里添加任何在导入模型前可能需要的预加载关系是一个很好的地方：

```php
use Illuminate\Database\Eloquent\Builder;

/**
 * 修改用于检索模型的查询，以便将所有模型设为可搜索。
 */
protected function makeAllSearchableUsing(Builder $query): Builder
{
    return $query->with('author');
}
```

> [!警告]
> 当使用队列批量导入模型时，`makeAllSearchableUsing` 方法可能不适用。模型集合被作业处理时，关系 **不会恢复** [不恢复关系](/docs/laravel/12.x/queues#handling-relationships)。



### 添加记录

一旦你在模型中添加了 `Laravel\Scout\Searchable` trait，你只需 `save` 或 `create` 一个模型实例，它就会自动被添加到你的搜索索引中。如果你已配置 Scout 使用队列，此操作将由队列工作器在后台执行：

```php
use App\Models\Order;

$order = new Order;

// ...

$order->save();
```

#### 通过查询添加记录

如果你想通过 Eloquent 查询将一组模型添加到搜索索引中，可以在 Eloquent 查询上链式调用 `searchable` 方法。`searchable` 方法会 [分块处理查询结果](/docs/laravel/12.x/eloquent#chunking-results) 并将记录添加到搜索索引中。同样地，如果你配置了 Scout 使用队列，所有的分块都会由队列工作器在后台导入：

```php
use App\Models\Order;

Order::where('price', '>', 100)->searchable();
```

你也可以在 Eloquent 关系实例上调用 `searchable` 方法：

```php
$user->orders()->searchable();
```

或者，如果你已经在内存中有一个 Eloquent 模型集合，可以在集合实例上调用 `searchable` 方法，将模型实例添加到对应的索引中：

```php
$orders->searchable();
```

> [!注意]
> `searchable` 方法可以被视为“upsert”操作。换句话说，如果模型记录已存在于索引中，它会被更新；如果索引中不存在，它将被添加到索引中。



### 更新记录

要更新一个可搜索模型，你只需更新模型实例的属性并将模型 `save` 到数据库中。Scout 会自动将更改同步到你的搜索索引：

```php
use App\Models\Order;

$order = Order::find(1);

// 更新订单...

$order->save();
```

你也可以在 Eloquent 查询实例上调用 `searchable` 方法来更新一组模型。如果模型在搜索索引中不存在，它们将被创建：

```php
Order::where('price', '>', 100)->searchable();
```

如果你想更新某个关系中所有模型的搜索索引记录，可以在关系实例上调用 `searchable` 方法：

```php
$user->orders()->searchable();
```

或者，如果你已经在内存中有一个 Eloquent 模型集合，可以在集合实例上调用 `searchable` 方法，更新模型在对应索引中的记录：

```php
$orders->searchable();
```

#### 在导入前修改记录

有时，你可能需要在将模型设为可搜索之前对模型集合进行准备。例如，你可能希望预加载某个关系，以便关系数据可以高效地添加到搜索索引中。为此，可以在对应模型中定义 `makeSearchableUsing` 方法：

```php
use Illuminate\Database\Eloquent\Collection;

/**
 * 修改正在设为可搜索的模型集合。
 */
public function makeSearchableUsing(Collection $models): Collection
{
    return $models->load('author');
}
```

### 删除记录

要从索引中移除记录，你可以直接从数据库中 `delete` 模型。即使你使用的是 [软删除](/docs/laravel/12.x/eloquent#soft-deleting) 模型，也可以执行此操作：

```php
use App\Models\Order;

$order = Order::find(1);

$order->delete();
```



如果你不想在删除记录之前先检索模型，可以在 Eloquent 查询实例上使用 `unsearchable` 方法：

```php
Order::where('price', '>', 100)->unsearchable();
```

如果你想删除某个关系中所有模型的搜索索引记录，可以在关系实例上调用 `unsearchable` 方法：

```php
$user->orders()->unsearchable();
```

或者，如果你已经在内存中有一个 Eloquent 模型集合，可以在集合实例上调用 `unsearchable` 方法，将模型实例从对应的索引中移除：

```php
$orders->unsearchable();
```

要从对应索引中移除所有模型记录，可以调用 `removeAllFromSearch` 方法：

```php
Order::removeAllFromSearch();
```

### 暂停索引同步

有时，你可能需要对模型执行一批 Eloquent 操作，而不将模型数据同步到搜索索引。你可以使用 `withoutSyncingToSearch` 方法来实现。此方法接受一个闭包，并立即执行。闭包内发生的任何模型操作都不会同步到模型的索引：

```php
use App\Models\Order;

Order::withoutSyncingToSearch(function () {
  // 执行模型操作...
});
```

### 条件可搜索的模型实例

有时，你可能只希望在特定条件下将模型设为可搜索。例如，假设你有 `App\Models\Post` 模型，它可能处于两种状态之一：“draft”（草稿）和 “published”（已发布）。你可能只希望“已发布”的文章可被搜索。为此，你可以在模型中定义 `shouldBeSearchable` 方法：

```php
/**
 * 确定模型是否应可搜索。
 */
public function shouldBeSearchable(): bool
{
    return $this->isPublished();
}
```



`shouldBeSearchable` 方法仅在通过 `save` 和 `create` 方法、查询或关系操作模型时生效。直接使用 `searchable` 方法使模型或集合可搜索时，会覆盖 `shouldBeSearchable` 方法的结果。

> [!WARNING]
> 当使用 Scout 的“数据库”引擎时，`shouldBeSearchable` 方法不适用，因为所有可搜索数据始终存储在数据库中。要在使用数据库引擎时实现类似行为，应使用 [where 子句](#where-clauses)。

## 搜索

你可以使用 `search` 方法开始对模型进行搜索。`search` 方法接受一个字符串，用于搜索模型。然后，你应该在搜索查询上链式调用 `get` 方法，以获取匹配给定搜索查询的 Eloquent 模型：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->get();
```

由于 Scout 搜索返回的是 Eloquent 模型的集合，你甚至可以直接从路由或控制器返回结果，它们会自动转换为 JSON：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/search', function (Request $request) {
    return Order::search($request->search)->get();
});
```

如果你希望在将结果转换为 Eloquent 模型之前获取原始搜索结果，可以使用 `raw` 方法：

```php
$orders = Order::search('Star Trek')->raw();
```

#### 自定义索引

搜索查询通常会在模型的 [searchableAs](#configuring-model-indexes) 方法指定的索引上执行。但是，你可以使用 `within` 方法指定一个自定义索引来进行搜索：

```php
$orders = Order::search('Star Trek')
    ->within('tv_shows_popularity_desc')
    ->get();
```



### Where 子句

Scout 允许你在搜索查询中添加简单的 “where” 子句。目前，这些子句仅支持基本的数值相等检查，主要用于按所有者 ID 限制搜索查询：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->where('user_id', 1)->get();
```

此外，可以使用 `whereIn` 方法来验证某列的值是否包含在给定数组中：

```php
$orders = Order::search('Star Trek')->whereIn(
    'status', ['open', 'paid']
)->get();
```

`whereNotIn` 方法用于验证某列的值是否不包含在给定数组中：

```php
$orders = Order::search('Star Trek')->whereNotIn(
    'status', ['closed']
)->get();
```

由于搜索索引不是关系型数据库，目前不支持更高级的 “where” 子句。

> [!警告]
> 如果你的应用使用 Meilisearch，你必须在使用 Scout 的 “where” 子句之前，配置应用的 [可过滤属性](#configuring-filterable-data-for-meilisearch)。

### 分页

除了获取模型集合之外，你还可以使用 `paginate` 方法对搜索结果进行分页。此方法会返回一个 `Illuminate\Pagination\LengthAwarePaginator` 实例，就像你对传统 Eloquent 查询进行分页一样：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->paginate();
```

你可以通过将每页要检索的模型数量作为 `paginate` 方法的第一个参数来指定每页数量：

```php
$orders = Order::search('Star Trek')->paginate(15);
```

一旦获取到结果，你可以像分页传统 Eloquent 查询一样，使用 [Blade](/docs/laravel/12.x/blade) 显示结果并渲染分页链接：

```html
<div class="container">
    @foreach ($orders as $order)
        {{ $order->price }}
    @endforeach
</div>

{{ $orders->links() }}
```



当然，如果你希望以 JSON 格式获取分页结果，可以直接从路由或控制器返回分页器实例：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/orders', function (Request $request) {
    return Order::search($request->input('query'))->paginate(15);
});
```

> [!警告]
> 由于搜索引擎无法感知你的 Eloquent 模型的全局作用域定义，因此在使用 Scout 分页的应用中，不应使用全局作用域。或者，你需要在通过 Scout 搜索时重新创建全局作用域的约束条件。

### 软删除（Soft Deleting）

如果你的索引模型是 [软删除](/docs/laravel/12.x/eloquent#soft-deleting) 的，并且你需要搜索软删除的模型，请在 `config/scout.php` 配置文件中将 `soft_delete` 选项设置为 `true`：

```php
'soft_delete' => true,
```

当此配置选项为 `true` 时，Scout 不会将软删除的模型从搜索索引中移除。相反，它会在索引记录上设置一个隐藏的 `__soft_deleted` 属性。然后，你可以使用 `withTrashed` 或 `onlyTrashed` 方法在搜索时检索软删除记录：

```php
use App\Models\Order;

// 检索结果时包含被软删除的记录...
$orders = Order::search('Star Trek')->withTrashed()->get();

// 检索结果时仅包含被软删除的记录...
$orders = Order::search('Star Trek')->onlyTrashed()->get();
```

> [!注意]
> 当软删除模型被使用 `forceDelete` 永久删除时，Scout 会自动将其从搜索索引中移除。

### 自定义引擎搜索（Customizing Engine Searches）

如果你需要对搜索引擎的搜索行为进行高级自定义，可以在 `search` 方法中将闭包作为第二个参数传入。例如，你可以使用该回调在搜索查询传递给 Algolia 之前，将地理位置数据添加到搜索选项中：

```php
use Algolia\AlgoliaSearch\SearchIndex;
use App\Models\Order;

Order::search(
    'Star Trek',
    function (SearchIndex $algolia, string $query, array $options) {
        $options['body']['query']['bool']['filter']['geo_distance'] = [
            'distance' => '1000km',
            'location' => ['lat' => 36, 'lon' => 111],
        ];

        return $algolia->search($query, $options);
    }
)->get();
```



#### 自定义 Eloquent 结果查询

在 Scout 从应用程序的搜索引擎中检索到匹配的 Eloquent 模型列表后，Eloquent 会根据主键检索所有匹配的模型。你可以通过调用 `query` 方法来自定义此查询。`query` 方法接受一个闭包，该闭包会接收 Eloquent 查询构建器实例作为参数：

```php
use App\Models\Order;
use Illuminate\Database\Eloquent\Builder;

$orders = Order::search('Star Trek')
    ->query(fn (Builder $query) => $query->with('invoices'))
    ->get();
```

由于该回调是在相关模型已从应用程序的搜索引擎中检索之后调用的，因此 `query` 方法不应用于“过滤”结果。相反，你应该使用 [Scout 的 where 子句](#where-clauses)。

## 自定义引擎

#### 编写引擎

如果内置的 Scout 搜索引擎不能满足你的需求，你可以编写自己的自定义引擎并将其注册到 Scout。你的引擎应继承 `Laravel\Scout\Engines\Engine` 抽象类。该抽象类包含你的自定义引擎必须实现的八个方法：

```php
use Laravel\Scout\Builder;

abstract public function update($models);
abstract public function delete($models);
abstract public function search(Builder $builder);
abstract public function paginate(Builder $builder, $perPage, $page);
abstract public function mapIds($results);
abstract public function map(Builder $builder, $results, $model);
abstract public function getTotalCount($results);
abstract public function flush($model);
```

你可能会发现，查看 `Laravel\Scout\Engines\AlgoliaEngine` 类中这些方法的实现非常有帮助。该类将为你提供一个很好的起点，帮助你了解如何在自己的引擎中实现每一个方法。



#### 注册引擎

在你编写完自定义引擎后，可以使用 Scout 引擎管理器的 `extend` 方法将其注册到 Scout。Scout 的引擎管理器可以从 Laravel 服务容器中解析。你应该在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中，或者在应用程序使用的任何其他服务提供者中调用 `extend` 方法：

```php
use App\ScoutExtensions\MySqlSearchEngine;
use Laravel\Scout\EngineManager;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    resolve(EngineManager::class)->extend('mysql', function () {
        return new MySqlSearchEngine;
    });
}
```

一旦你的引擎被注册，你可以在应用程序的 `config/scout.php` 配置文件中将其指定为默认的 Scout `driver`：

```php
'driver' => 'mysql',
```
