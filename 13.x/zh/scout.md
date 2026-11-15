# Laravel Scout

- [简介](#introduction)
- [安装](#installation)
    - [队列](#queueing)
- [驱动先决条件](#driver-prerequisites)
    - [Algolia](#algolia)
    - [Meilisearch](#meilisearch)
    - [Typesense](#typesense)
    - [Turbopuffer](#turbopuffer)
- [配置](#configuration)
    - [配置可搜索数据](#configuring-searchable-data)
- [数据库 / 集合引擎](#database-and-collection-engines)
    - [数据库引擎](#database-engine)
    - [集合引擎](#collection-engine)
- [第三方引擎配置](#third-party-engine-configuration)
    - [配置模型索引](#configuring-model-indexes)
    - [Algolia](#algolia-configuration)
    - [Meilisearch](#meilisearch-configuration)
    - [Typesense](#typesense-configuration)
    - [Turbopuffer](#turbopuffer-configuration)
- [第三方引擎索引](#indexing)
    - [批量导入](#batch-import)
    - [添加记录](#adding-records)
    - [更新记录](#updating-records)
    - [移除记录](#removing-records)
    - [暂停索引](#pausing-indexing)
    - [有条件的可搜索模型实例](#conditionally-searchable-model-instances)
- [搜索](#searching)
    - [Where 子句](#where-clauses)
    - [语义搜索](#semantic-search)
    - [分页](#pagination)
    - [软删除](#soft-deleting)
    - [自定义引擎搜索](#customizing-engine-searches)
- [自定义引擎](#custom-engines)

<a name="introduction"></a>
## 简介

[Laravel Scout](https://github.com/laravel/scout) 提供了一种基于驱动的简单方案，为 [Eloquent 模型](/docs/{{version}}/eloquent) 添加全文搜索功能。Scout 使用模型观察器，自动保持搜索索引与 Eloquent 记录同步。

Scout 内置的 `database` 引擎使用 MySQL / PostgreSQL 全文索引和 `LIKE` 子句直接搜索现有数据库，无需外部服务。对于大多数应用来说，这已经足够。有关 Laravel 中所有搜索选项的概览，请参阅 [搜索文档](/docs/{{version}}/search)。

当你需要容错、分面筛选、向量搜索或大规模地理搜索等功能时，Scout 还提供 [Algolia](https://www.algolia.com/)、[Meilisearch](https://www.meilisearch.com)、[Typesense](https://typesense.org) 和 [Turbopuffer](https://turbopuffer.com) 驱动。另外还有用于本地开发的「collection」驱动，你也可以编写 [自定义引擎](#custom-engines)。

<a name="installation"></a>
## 安装

首先，通过 Composer 包管理器安装 Scout：

```shell
composer require laravel/scout
```

安装 Scout 后，应使用 `vendor:publish` Artisan 命令发布 Scout 配置文件。该命令会将 `scout.php` 配置文件发布到应用的 `config` 目录：

```shell
php artisan vendor:publish --provider="Laravel\Scout\ScoutServiceProvider"
```

最后，将 `Laravel\Scout\Searchable` trait 添加到需要搜索的模型中。该 trait 会注册一个模型观察器，自动保持模型与搜索驱动同步：

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

<a name="queueing"></a>
### 队列

使用 `database` 或 `collection` 以外的引擎时，强烈建议在使用该库之前配置 [队列驱动](/docs/{{version}}/queues)。运行队列工作进程后，Scout 就可以将所有同步模型信息到搜索索引的操作放入队列，从而显著缩短应用 Web 界面的响应时间。

配置队列驱动后，将 `config/scout.php` 配置文件中的 `queue` 选项设为 `true`：

```php
'queue' => true,
```

即使将 `queue` 选项设为 `false`，也要注意 Algolia 和 Meilisearch 等部分 Scout 驱动始终异步索引记录。也就是说，即使索引操作已在 Laravel 应用中完成，搜索引擎本身也可能不会立即反映新增或更新的记录。

要指定 Scout 作业使用的连接和队列，可以将 `queue` 配置选项定义为数组：

```php
'queue' => [
    'connection' => 'redis',
    'queue' => 'scout'
],
```

当然，如果自定义了 Scout 作业使用的连接和队列，应运行队列工作进程来处理该连接和队列上的作业：

```shell
php artisan queue:work redis --queue=scout
```

<a name="unique-jobs"></a>
#### 唯一作业

在写入频繁的应用中，你可能希望防止 Scout 为相同的模型记录重复排队作业。可以注册 `MakeSearchableUniquely` 和 `RemoveFromSearchUniquely` 作业类来启用唯一索引作业，通常在服务提供者的 `boot` 方法中注册：

```php
use Laravel\Scout\Jobs\MakeSearchableUniquely;
use Laravel\Scout\Jobs\RemoveFromSearchUniquely;
use Laravel\Scout\Scout;

Scout::makeSearchableUsing(MakeSearchableUniquely::class);
Scout::removeFromSearchUsing(RemoveFromSearchUniquely::class);
```

这些作业使用 Laravel 的 [唯一作业锁](/docs/{{version}}/queues#unique-jobs)，在匹配的作业已进入队列时，避免为相同的可搜索模型记录分派重复的索引队列作业。

<a name="driver-prerequisites"></a>
## 驱动先决条件

<a name="algolia"></a>
### Algolia

使用 Algolia 驱动时，应在 `config/scout.php` 配置文件中配置 Algolia 的 `id` 和 `secret` 凭证。配置好凭证后，还需要通过 Composer 包管理器安装 Algolia PHP SDK：

```shell
composer require algolia/algoliasearch-client-php
```

<a name="meilisearch"></a>
### Meilisearch

[Meilisearch](https://www.meilisearch.com) 是一个快速的开源搜索引擎，支持全文、语义和混合搜索。如果不确定如何在本地安装 Meilisearch，可以使用 Laravel 官方支持的 Docker 开发环境 [Laravel Sail](/docs/{{version}}/sail#meilisearch)。在生产环境中，你可以 [自行托管](https://www.meilisearch.com/docs/learn/self_hosted/getting_started_with_self_hosted_meilisearch) Meilisearch 或使用 [Meilisearch Cloud](https://www.meilisearch.com/cloud)。

使用 Meilisearch 驱动时，需要通过 Composer 包管理器安装 Meilisearch PHP SDK：

```shell
composer require meilisearch/meilisearch-php http-interop/http-factory-guzzle
```

然后，在应用的 `.env` 文件中设置 `SCOUT_DRIVER` 环境变量以及 Meilisearch 的 `host` 和 `key` 凭证：

```ini
SCOUT_DRIVER=meilisearch
MEILISEARCH_HOST=http://127.0.0.1:7700
MEILISEARCH_KEY=masterKey
```

有关 Meilisearch 的更多信息，请参阅 [Meilisearch 文档](https://www.meilisearch.com/docs/getting_started/overview)。

<a name="typesense"></a>
### Typesense

[Typesense](https://typesense.org) 是一个速度极快的开源搜索引擎，支持关键词搜索、语义搜索、地理搜索和向量搜索。

你可以 [自行托管](https://typesense.org/docs/guide/install-typesense.html#option-2-local-machine-self-hosting) Typesense 或使用 [Typesense Cloud](https://cloud.typesense.org)。

要在 Scout 中使用 Typesense，请通过 Composer 包管理器安装 Typesense PHP SDK：

```shell
composer require typesense/typesense-php
```

然后，在应用的 .env 文件中设置 `SCOUT_DRIVER` 环境变量以及 Typesense 主机和 API 密钥凭证：

```ini
SCOUT_DRIVER=typesense
TYPESENSE_API_KEY=masterKey
TYPESENSE_HOST=localhost
```

如果使用 [Laravel Sail](/docs/{{version}}/sail)，你可能需要调整 `TYPESENSE_HOST` 环境变量以匹配 Docker 容器名称。你也可以选择指定安装实例的端口、路径和协议：

```ini
TYPESENSE_PORT=8108
TYPESENSE_PATH=
TYPESENSE_PROTOCOL=http
```

Typesense 集合的其他设置和模式定义可在应用的 `config/scout.php` 配置文件中找到。有关 Typesense 的更多信息，请参阅 [Typesense 文档](https://typesense.org/docs/guide/#quick-start)。

<a name="turbopuffer"></a>
### Turbopuffer

[Turbopuffer](https://turbopuffer.com) 是一个支持全文、语义和混合搜索的搜索引擎。要使用 Turbopuffer 驱动，请设置 `SCOUT_DRIVER` 环境变量并提供 Turbopuffer API 密钥：

```ini
SCOUT_DRIVER=turbopuffer
TURBOPUFFER_API_KEY=tpuf_...
TURBOPUFFER_REGION=gcp-us-central1
```

`TURBOPUFFER_REGION` 环境变量是可选的，默认为 `gcp-us-central1`。

<a name="configuration"></a>
## 配置

<a name="configuring-searchable-data"></a>
### 配置可搜索数据

默认情况下，给定模型的完整 `toArray` 形式会被保存到其搜索索引中。如果要自定义同步到搜索索引的数据，可以在模型上重写 `toSearchableArray` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Post extends Model
{
    use Searchable;

    /**
     * 获取模型的可索引数据数组。
     *
     * @return array<string, mixed>
     */
    public function toSearchableArray(): array
    {
        $array = $this->toArray();

        // 自定义数据数组……

        return $array;
    }
}
```

<a name="configuring-search-engines-per-model"></a>
#### 配置模型搜索引擎

搜索时，Scout 通常使用应用的 `scout` 配置文件中指定的默认搜索引擎。不过，可以通过重写模型的 `searchableUsing` 方法来更改特定模型使用的搜索引擎：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Engines\Engine;
use Laravel\Scout\Scout;
use Laravel\Scout\Searchable;

class User extends Model
{
    use Searchable;

    /**
     * 获取用于索引模型的引擎。
     */
    public function searchableUsing(): Engine
    {
        return Scout::engine('meilisearch');
    }
}
```

<a name="database-and-collection-engines"></a>
## 数据库 / 集合引擎

<a name="database-engine"></a>
### 数据库引擎

> [!WARNING]
> 数据库引擎目前支持 MySQL 和 PostgreSQL，两者都支持快速的列全文索引。

`database` 引擎使用 MySQL / PostgreSQL 全文索引和 `LIKE` 子句直接搜索现有数据库。对于许多应用来说，这是添加搜索功能最简单、最实用的方式，无需外部服务或额外基础设施。

要使用数据库引擎，请将 `SCOUT_DRIVER` 环境变量设为 `database`：

```ini
SCOUT_DRIVER=database
```

配置完成后，即可 [定义可搜索数据](#configuring-searchable-data)，并开始对模型 [执行搜索查询](#searching)。与第三方引擎不同，数据库引擎无需单独的索引步骤，它会直接搜索数据库表。

<a name="database-semantic-and-hybrid-search"></a>
#### 语义与混合搜索

使用带有 `pgvector` 扩展的 PostgreSQL 时，数据库引擎支持语义搜索和混合搜索。首先，为模型表添加一个可为空的向量列和一个全文索引。由于 Scout 在模型持久化后才存储嵌入向量，该向量列必须允许为空：

```php
Schema::ensureVectorExtensionExists();

Schema::table('articles', function (Blueprint $table) {
    // ...

    $table->vector('embedding', dimensions: 1536)->nullable();
    $table->vectorIndex('embedding');
    $table->fullText(['title', 'body']);
});
```

接下来，在模型上定义 `toSearchableEmbedding` 方法。该方法可以返回 Scout 应生成嵌入向量的源文本，也可以返回预先计算的嵌入向量数组。Scout 默认将嵌入向量存储在 `embedding` 列中；要使用其他列，请在模型上定义 `searchableEmbeddingColumn` 方法。

#### 自定义数据库搜索策略

默认情况下，数据库引擎会对每个 [配置为可搜索](#configuring-searchable-data) 的模型属性执行 `LIKE` 查询。不过，你可以为特定列指定更高效的搜索策略。`SearchUsingFullText` 属性使用数据库中该列的全文索引，而 `SearchUsingPrefix` 仅匹配字符串开头（`example%`），而不是搜索整个字符串（`%example%`）。

要定义此行为，请为模型的 `toSearchableArray` 方法添加 PHP 属性。未指定属性的列将继续使用默认的 `LIKE` 策略：

```php
use Laravel\Scout\Attributes\SearchUsingFullText;
use Laravel\Scout\Attributes\SearchUsingPrefix;

/**
 * 获取模型的可索引数据数组。
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

> [!WARNING]
> 指定列使用全文查询约束之前，请确保该列已创建 [全文索引](/docs/{{version}}/migrations#available-index-types)。

<a name="postgresql-full-text-search"></a>
#### PostgreSQL 全文搜索

使用 PostgreSQL 时，Scout 可以搜索存储的 `tsvector` 列，以实现带索引和权重的全文搜索。首先，在迁移中使用 `searchable` 方法添加生成的 `search_vector` 列及其 GIN 索引：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('posts', function (Blueprint $table) {
    $table->searchable(['title' => 'A', 'body' => 'D']);
});
```

列权重从 `A`（最高）到 `D`（最低）。你也可以传入不带权重的列名列表，例如 `['title', 'body']`，为每列分配默认权重 `D`。源列发生变化时，PostgreSQL 会自动更新生成的列。

接下来，将 `SearchUsingFullText` 属性应用于模型的 `toSearchableArray` 方法，并将 `vector` 选项设为 `true`：

```php
use Laravel\Scout\Attributes\SearchUsingFullText;

/**
 * 获取模型的可索引数据数组。
 *
 * @return array<string, mixed>
 */
#[SearchUsingFullText(['search_vector'], ['vector' => true])]
public function toSearchableArray(): array
{
    return ['search_vector' => null];
}
```

只需提供列名，Scout 会直接搜索存储的值。请仅返回向量列，以免为其他属性添加 `LIKE` 子句，导致 PostgreSQL 无法使用 GIN 索引。

`searchable` 方法还接受文本搜索配置、三元组索引列和自定义向量列名：

```php
$table->searchable(
    columns: ['title' => 'A', 'body' => 'D'],
    language: 'english',
    trigram: ['title'],
    tsvector: 'search_vector',
);
```

要在回滚迁移时删除生成的列及其索引，请使用 `dropSearchable` 方法，并传入相同的三元组列和向量列名：

```php
Schema::table('posts', function (Blueprint $table) {
    $table->dropSearchable(trigram: ['title'], tsvector: 'search_vector');
});
```

#### PostgreSQL 搜索选项

可以通过 `SearchUsingFullText` 属性的第二个参数自定义 PostgreSQL 全文搜索：

| Option | Description | Default |
| --- | --- | --- |
| `vector` | Whether the full-text columns are stored `tsvector` columns. | `false` |
| `language` | The text search configuration, such as `english` or `public.english_unaccent`. | `english` |
| `mode` | The query syntax: `plain`, `phrase`, `websearch`, or `raw`. | `plain` |
| `rank` | The ranking function: `ts_rank` or `ts_rank_cd`. | `ts_rank` |
| `trigram` | A column name or array of columns for typo-tolerant matching. | None |
| `trigram_mode` | Whether trigram matching is used as a `fallback` or blended with full-text matches using `blend`. | `fallback` |

`plain` 模式搜索所有查询词，而 `phrase` 按顺序匹配词语。`websearch` 模式支持网页搜索语法，例如带引号的短语和排除词；`raw` 则接受 PostgreSQL `tsquery` 语法。搜索存储的向量列时，`language` 必须与生成该列时使用的文本搜索配置一致。

要启用拼写容错，请在迁移和属性选项中都指定三元组列：

```php
#[SearchUsingFullText(['search_vector'], ['vector' => true, 'trigram' => ['title']])]
public function toSearchableArray(): array
{
    return ['search_vector' => null];
}
```

默认情况下，Scout 仅在首次搜索没有结果时才使用三元组匹配重试。将 `trigram_mode` 设为 `blend`，即可将三元组匹配与全文匹配一并纳入结果，并将三元组相似度计入相关性排名。

> [!WARNING]
> 三元组匹配要求 `pg_trgm` 扩展在连接的搜索路径中可用。提供三元组列时，`searchable` 迁移方法会创建该扩展，因此运行迁移的数据库用户必须有权创建扩展。

你可以使用 `options` 方法，为单次搜索覆盖 `mode`、`language`、`rank`、`trigram` 和 `trigram_mode` 选项：

```php
$posts = Post::search('"laravel scout"')->options(['mode' => 'websearch'])->get();
```

<a name="collection-engine"></a>
### 集合引擎

「collection」引擎适用于快速原型、极小的数据集（数百条记录）或运行测试。它从数据库中检索所有可能的记录，并使用 Laravel 的 `Str::is` 辅助函数在 PHP 中筛选，因此不需要任何索引或特定数据库功能。对于非简单场景，应改用 [数据库引擎](#database-engine)。

要使用集合引擎，只需将 `SCOUT_DRIVER` 环境变量设为 `collection`，或者在应用的 `scout` 配置文件中直接指定 `collection` 驱动：

```ini
SCOUT_DRIVER=collection
```

将集合驱动设为首选驱动后，即可开始对模型 [执行搜索查询](#searching)。使用集合引擎时，无需进行搜索引擎索引，例如填充 Algolia、Meilisearch 或 Typesense 索引所需的索引操作。

#### 与数据库引擎的区别

数据库引擎使用全文索引和 `LIKE` 子句高效查找匹配记录，而集合引擎会取出所有记录并在 PHP 中筛选。集合引擎具有最好的可移植性，因为它适用于 Laravel 支持的所有关系数据库（包括 SQLite 和 SQL Server）；但其效率明显低于数据库引擎，不应在大型数据集上使用。

<a name="third-party-engine-configuration"></a>
## 第三方引擎配置

以下配置选项仅与 Algolia、Meilisearch 或 Typesense 等第三方搜索引擎有关。如果使用 [数据库引擎](#database-engine)，可以跳过本节。

<a name="configuring-model-indexes"></a>
### 配置模型索引

使用第三方引擎时，每个 Eloquent 模型都与一个搜索「索引」同步，该索引包含模型的所有可搜索记录。默认情况下，每个模型都会保存到与其常规模型「表」名称相同的索引中，通常是模型名称的复数形式；你也可以通过重写模型的 `searchableAs` 方法自定义索引：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Post extends Model
{
    use Searchable;

    /**
     * 获取与模型关联的索引名称。
     */
    public function searchableAs(): string
    {
        return 'posts_index';
    }
}
```

> [!NOTE]
> 使用数据库引擎时，`searchableAs` 方法没有效果，因为数据库引擎始终直接搜索模型的数据库表。

<a name="configuring-the-model-id"></a>
#### 配置模型 ID

默认情况下，Scout 使用模型主键作为存储在搜索索引中的唯一 ID / 键。使用第三方引擎时，如果需要自定义此行为，可以重写模型的 `getScoutKey` 和 `getScoutKeyName` 方法：

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

> [!NOTE]
> 使用数据库引擎时，`getScoutKey` 和 `getScoutKeyName` 方法没有效果，因为数据库引擎始终使用模型主键。

<a name="algolia-configuration"></a>
### Algolia

<a name="algolia-index-settings"></a>
#### 索引设置

有时，你可能需要为 Algolia 索引配置额外设置。虽然可以通过 Algolia 界面管理这些设置，但直接在应用的 `config/scout.php` 配置文件中管理索引配置的期望状态有时更加高效。

这种方式允许你通过应用的自动化部署流水线部署这些设置，避免手动配置，并确保多个环境保持一致。你可以配置可筛选属性、排名、分面或 [其他受支持的设置](https://www.algolia.com/doc/rest-api/search/#tag/Indices/operation/setSettings)。

首先，在应用的 `config/scout.php` 配置文件中为每个索引添加设置：

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
            // 其他设置字段……
        ],
        Flight::class => [
            'searchableAttributes'=> ['id', 'destination'],
        ],
    ],
],
```

如果某个索引对应的模型支持软删除，且包含在 `index-settings` 数组中，Scout 会自动为该索引支持基于软删除模型的分面。如果不需要为可软删除模型的索引定义其他分面属性，可以在 `index-settings` 数组中为该模型添加一个空条目：

```php
'index-settings' => [
    Flight::class => []
],
```

配置应用的索引设置后，必须调用 `scout:sync-index-settings` Artisan 命令。此命令会将当前配置的索引设置告知 Algolia。为了方便，你可以将此命令加入部署流程：

```shell
php artisan scout:sync-index-settings
```

<a name="algolia-identifying-users"></a>
#### 识别用户

Scout 允许在使用 Algolia 时自动识别用户。将已认证用户与搜索操作关联，有助于在 Algolia 控制面板中查看搜索分析数据。可以在应用的 `.env` 文件中将 `SCOUT_IDENTIFY` 环境变量设为 `true` 来启用用户识别：

```ini
SCOUT_IDENTIFY=true
```

启用此功能还会将请求的 IP 地址和已认证用户的主标识符传递给 Algolia，从而将这些数据与该用户发起的所有搜索请求关联。

<a name="meilisearch-configuration"></a>
### Meilisearch

<a name="meilisearch-index-settings"></a>
#### 索引设置

Meilisearch 要求预先定义索引搜索设置，例如可筛选属性、可排序属性和 [其他支持的设置字段](https://docs.meilisearch.com/reference/api/settings.html)。

可筛选属性是调用 Scout 的 `where` 方法时计划用于筛选的属性，而可排序属性是调用 Scout 的 `orderBy` 方法时计划用于排序的属性。要定义索引设置，请调整应用 `scout` 配置文件中 `meilisearch` 配置项的 `index-settings` 部分：

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
            // 其他设置字段……
        ],
        Flight::class => [
            'filterableAttributes'=> ['id', 'destination'],
            'sortableAttributes' => ['updated_at'],
        ],
    ],
],
```

如果某个索引对应的模型支持软删除，且包含在 `index-settings` 数组中，Scout 会自动为该索引支持按软删除模型筛选。如果不需要为可软删除模型的索引定义其他可筛选或可排序属性，可以在 `index-settings` 数组中为该模型添加一个空条目：

```php
'index-settings' => [
    Flight::class => []
],
```

配置应用的索引设置后，必须调用 `scout:sync-index-settings` Artisan 命令。此命令会将当前配置的索引设置告知 Meilisearch。为了方便，你可以将此命令加入部署流程：

```shell
php artisan scout:sync-index-settings
```

<a name="meilisearch-semantic-and-hybrid-search"></a>
#### 语义与混合搜索

要使用 Meilisearch 进行语义或混合搜索，请在索引设置中配置嵌入器，并为每个可搜索模型配置嵌入设置：

```php
'meilisearch' => [
    // ...
    'index-settings' => [
        Article::class => [
            'embedders' => [
                'default' => [
                    'source' => 'userProvided',
                    'dimensions' => 1536,
                ],
            ],
        ],
    ],
    'model-settings' => [
        Article::class => [
            'embedding' => [
                'embedder' => 'default',
                'dimensions' => 1536,
            ],
        ],
    ],
],
```

模型的 `toSearchableEmbedding` 方法可以返回源文本，由 Scout 使用 [Laravel AI SDK](/docs/{{version}}/ai-sdk) 生成嵌入向量，也可以返回预先计算的嵌入向量数组。更新配置后，运行 `scout:sync-index-settings` 命令。

你也可以将嵌入的 `driver` 设为 `meilisearch`，使用 Meilisearch 原生嵌入。在此模式下，Meilisearch 使用配置的嵌入器生成文档和查询的嵌入向量，因此不需要 `dimensions` 选项和 `toSearchableEmbedding` 方法：

```php
'meilisearch' => [
    'index-settings' => [
        Article::class => [
            'embedders' => [
                'default' => [
                    'source' => 'openAi',
                    'apiKey' => env('OPENAI_API_KEY'),
                    'model' => 'text-embedding-3-small',
                    'documentTemplate' => 'An article titled {{ doc.title }}: {{ doc.body }}',
                ],
            ],
        ],
    ],
    'model-settings' => [
        Article::class => [
            'embedding' => [
                'embedder' => 'default',
                'driver' => 'meilisearch',
            ],
        ],
    ],
],
```

使用原生嵌入时，Scout 不会生成向量或将向量添加到索引文档。你仍可通过 `vector` 搜索选项提供预先计算的查询向量。与其他索引设置一样，更新嵌入器配置后请运行 `scout:sync-index-settings` 命令。

有关可用嵌入器来源及其选项的更多信息，请参阅 [Meilisearch 混合搜索文档](https://www.meilisearch.com/docs/capabilities/hybrid_search/getting_started)。

<a name="meilisearch-data-types"></a>
#### 可搜索数据类型

Meilisearch 只会对类型正确的数据执行筛选操作（`>`、`<` 等）。自定义可搜索数据时，应确保将数值转换为正确的类型：

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

<a name="typesense-configuration"></a>
### Typesense

<a name="typesense-searchable-data"></a>
#### 准备可搜索数据

使用 Typesense 时，可搜索模型必须定义 `toSearchableArray` 方法，将模型主键转换为字符串，并将创建日期转换为 UNIX 时间戳：

```php
/**
 * 获取模型的可索引数据数组。
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

还应在应用的 `config/scout.php` 文件中定义 Typesense 集合模式。集合模式描述了可通过 Typesense 搜索的各字段的数据类型。有关所有可用模式选项，请参阅 [Typesense 文档](https://typesense.org/docs/latest/api/collections.html#schema-parameters)。

如果需要修改已定义的 Typesense 集合模式，可以运行 `scout:flush` 和 `scout:import`，这会删除所有现有索引数据并重新创建模式；也可以使用 Typesense API 修改集合模式，而不删除任何索引数据。

如果可搜索模型支持软删除，应在应用的 `config/scout.php` 配置文件中，为该模型对应的 Typesense 模式定义 `__soft_deleted` 字段：

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

<a name="typesense-embeddings"></a>
#### 嵌入向量

要启用语义和混合搜索，请在模型的 Typesense 配置中定义 `embedding` 设置和向量字段。默认情况下，Scout 使用 [Laravel AI SDK](/docs/{{version}}/ai-sdk) 生成嵌入向量：

```php
use App\Models\Article;

'model-settings' => [
    Article::class => [
        'collection-schema' => [
            'fields' => [
                ['name' => 'title', 'type' => 'string'],
                ['name' => 'embedding', 'type' => 'float[]', 'num_dim' => 1536],
            ],
        ],
        'search-parameters' => ['query_by' => 'title'],
        'embedding' => [
            'attribute' => 'embedding',
            'dimensions' => 1536,
        ],
    ],
],
```

模型的 `toSearchableEmbedding` 方法应返回 Scout 要生成嵌入向量的源文本，或预先计算的嵌入向量数组：

```php
public function toSearchableEmbedding(): string|array
{
    return $this->title.' '.$this->body;
}
```

<a name="typesense-dynamic-search-parameters"></a>
#### 动态搜索参数

Typesense 允许你在执行搜索操作时通过 `options` 方法动态修改 [搜索参数](https://typesense.org/docs/latest/api/search.html#search-parameters)：

```php
use App\Models\Todo;

Todo::search('Groceries')->options([
    'query_by' => 'title, description'
])->get();
```

<a name="turbopuffer-configuration"></a>
### Turbopuffer

Turbopuffer 要求为每个模型定义模式和可搜索属性。请在 `scout` 配置文件的 `turbopuffer` 配置中，通过 `model-settings` 数组定义它们：

```php
use App\Models\Article;

'turbopuffer' => [
    // ...
    'model-settings' => [
        Article::class => [
            'searchable-attributes' => [
                'title' => 3,
                'body' => 1,
            ],
            'schema' => [
                'title' => ['type' => 'string', 'full_text_search' => true],
                'body' => ['type' => 'string', 'full_text_search' => true],
                'status' => ['type' => 'string'],
            ],
        ],
    ],
],
```

分配给 `searchable-attributes` 的数值是相对 BM25 权重。在上面的示例中，文章标题中的匹配贡献的分数是正文中匹配的三倍。

要启用语义和混合搜索，请在模型配置中添加 `embedding` 设置和向量模式：

```php
'turbopuffer' => [
    // ...
    'model-settings' => [
        Article::class => [
            'searchable-attributes' => [
                'title' => 3,
                'body' => 1,
            ],
            'embedding' => [
                'attribute' => 'embedding',
                'dimensions' => 1536,
            ],
            'schema' => [
                'title' => ['type' => 'string', 'full_text_search' => true],
                'body' => ['type' => 'string', 'full_text_search' => true],
                'embedding' => ['type' => '[1536]f32', 'ann' => true],
            ],
        ],
    ],
],
```

模型的 `toSearchableEmbedding` 方法应返回 Scout 要生成嵌入向量的源文本，或预先计算的嵌入向量数组。Scout 使用 [Laravel AI SDK](/docs/{{version}}/ai-sdk) 根据源文本生成嵌入向量。

你也可以使用 Turbopuffer 原生嵌入，而无需安装 Laravel AI SDK 或定义 `toSearchableEmbedding` 方法。将嵌入驱动设为 `turbopuffer`，并在可搜索的源属性上配置 `embed` 模式：

```php
'embedding' => [
    'driver' => 'turbopuffer',
    'attribute' => 'embedding_text',
],

'schema' => [
    // ...
    'embedding_text' => [
        'type' => 'string',
        'embed' => [
            'model' => 'voyage/voyage-4',
            'dimensions' => 1024,
            'attribute' => 'embedding',
        ],
    ],
],
```

源属性必须包含在模型的 `toSearchableArray` 输出中。

<a name="indexing"></a>
## 第三方引擎索引

> [!NOTE]
> 本节介绍的索引功能主要适用于 Algolia、Meilisearch、Typesense 或 Turbopuffer 等第三方引擎。数据库引擎直接搜索数据库表，因此不需要手动管理索引。

<a name="batch-import"></a>
### 批量导入

如果在现有项目中安装 Scout，可能已有需要导入索引的数据库记录。Scout 提供 `scout:import` Artisan 命令，可将所有现有记录导入搜索索引：

```shell
php artisan scout:import "App\Models\Post"
```

可以使用 `scout:queue-import` 命令通过 [队列作业](/docs/{{version}}/queues) 导入所有现有记录：

```shell
php artisan scout:queue-import "App\Models\Post" --chunk=500
```

可以使用 `flush` 命令从搜索索引中移除某个模型的所有记录：

```shell
php artisan scout:flush "App\Models\Post"
```

<a name="modifying-the-import-query"></a>
#### 修改导入查询

如果要修改批量导入时用于检索所有模型的查询，可以在模型上定义 `makeAllSearchableUsing` 方法。这个方法适合添加导入模型前可能需要的关系预加载：

```php
use Illuminate\Database\Eloquent\Builder;

/**
 * 修改将所有模型设为可搜索时用于检索模型的查询。
 */
protected function makeAllSearchableUsing(Builder $query): Builder
{
    return $query->with('author');
}
```

> [!WARNING]
> 使用队列批量导入模型时，`makeAllSearchableUsing` 方法可能不适用。作业处理模型集合时，[不会恢复](/docs/{{version}}/queues#handling-relationships) 关系。

<a name="adding-records"></a>
### 添加记录

为模型添加 `Laravel\Scout\Searchable` trait 后，只需 `save` 或 `create` 模型实例，它就会自动添加到搜索索引。如果已将 Scout 配置为 [使用队列](#queueing)，此操作将在后台由队列工作进程执行：

```php
use App\Models\Order;

$order = new Order;

// ...

$order->save();
```

<a name="adding-records-via-query"></a>
#### 通过查询添加记录

如果要通过 Eloquent 查询将模型集合添加到搜索索引，可以在 Eloquent 查询后链式调用 `searchable` 方法。`searchable` 方法会将查询结果 [分块](/docs/{{version}}/eloquent#chunking-results)，并将记录添加到搜索索引。同样，如果已配置 Scout 使用队列，所有块都会由队列工作进程在后台导入：

```php
use App\Models\Order;

Order::where('price', '>', 100)->searchable();
```

你也可以在 Eloquent 关系实例上调用 `searchable` 方法：

```php
$user->orders()->searchable();
```

或者，如果内存中已有 Eloquent 模型集合，可以在集合实例上调用 `searchable` 方法，将模型实例添加到对应索引：

```php
$orders->searchable();
```

> [!NOTE]
> `searchable` 方法可以视为「upsert」操作。也就是说，如果模型记录已在索引中，就会更新该记录；如果不存在，则会将其添加到索引中。

<a name="updating-records"></a>
### 更新记录

要更新可搜索模型，只需更新模型实例的属性，并将模型 `save` 到数据库。Scout 会自动将更改保存到搜索索引：

```php
use App\Models\Order;

$order = Order::find(1);

// 更新订单……

$order->save();
```

你也可以在 Eloquent 查询实例上调用 `searchable` 方法来更新模型集合。如果模型不存在于搜索索引中，则会创建相应记录：

```php
Order::where('price', '>', 100)->searchable();
```

如果要更新关系中所有模型的搜索索引记录，可以在关系实例上调用 `searchable` 方法：

```php
$user->orders()->searchable();
```

或者，如果内存中已有 Eloquent 模型集合，可以在集合实例上调用 `searchable` 方法，更新模型实例在对应索引中的记录：

```php
$orders->searchable();
```

<a name="modifying-records-before-importing"></a>
#### 导入前修改记录

有时，可能需要在模型集合变为可搜索之前对其进行准备。例如，你可能希望预加载某个关系，以便高效地将关系数据添加到搜索索引。为此，请在相应模型上定义 `makeSearchableUsing` 方法：

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

<a name="conditionally-updating-the-search-index"></a>
#### 有条件地更新搜索索引

默认情况下，无论修改了哪些属性，Scout 都会重新索引更新后的模型。如果要自定义此行为，可以在模型上定义 `searchIndexShouldBeUpdated` 方法：

```php
/**
 * 确定是否应更新搜索索引。
 */
public function searchIndexShouldBeUpdated(): bool
{
    return $this->wasRecentlyCreated || $this->wasChanged(['title', 'body']);
}
```

<a name="removing-records"></a>
### 移除记录

要从索引中移除记录，只需从数据库中 `delete` 模型。即使模型使用了 [软删除](/docs/{{version}}/eloquent#soft-deleting)，也可以这样做：

```php
use App\Models\Order;

$order = Order::find(1);

$order->delete();
```

如果不想在删除记录之前检索模型，可以在 Eloquent 查询实例上使用 `unsearchable` 方法：

```php
Order::where('price', '>', 100)->unsearchable();
```

如果要移除关系中所有模型的搜索索引记录，可以在关系实例上调用 `unsearchable` 方法：

```php
$user->orders()->unsearchable();
```

或者，如果内存中已有 Eloquent 模型集合，可以在集合实例上调用 `unsearchable` 方法，从对应索引中移除这些模型实例：

```php
$orders->unsearchable();
```

要从对应索引中移除模型的所有记录，可以调用 `removeAllFromSearch` 方法：

```php
Order::removeAllFromSearch();
```

<a name="pausing-indexing"></a>
### 暂停索引

有时，你可能需要对模型执行一批 Eloquent 操作，而不将模型数据同步到搜索索引。可以使用 `withoutSyncingToSearch` 方法。该方法接受一个立即执行的闭包，闭包中的模型操作不会同步到模型的索引：

```php
use App\Models\Order;

Order::withoutSyncingToSearch(function () {
    // 执行模型操作……
});
```

<a name="conditionally-searchable-model-instances"></a>
### 有条件的可搜索模型实例

有时，你可能只希望模型在满足特定条件时才可搜索。例如，假设 `App\Models\Post` 模型有「草稿」和「已发布」两种状态，你可能只希望允许搜索「已发布」的文章。为此，可以在模型上定义 `shouldBeSearchable` 方法：

```php
/**
 * 确定模型是否应可搜索。
 */
public function shouldBeSearchable(): bool
{
    return $this->isPublished();
}
```

`shouldBeSearchable` 方法仅在通过 `save` 和 `create` 方法、查询或关系操作模型时生效。直接使用 `searchable` 方法使模型或集合可搜索，会覆盖 `shouldBeSearchable` 方法的结果。

> [!WARNING]
> `shouldBeSearchable` 方法不适用于 Scout 的「database」引擎，因为所有可搜索数据始终存储在数据库中。使用数据库引擎时，要实现类似行为，应改用 [where 子句](#where-clauses)。

<a name="searching"></a>
## 搜索

可以使用 `search` 方法开始搜索模型。该方法接受一个用于搜索模型的字符串。然后，应在搜索查询后链式调用 `get` 方法，以获取符合给定搜索查询的 Eloquent 模型：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->get();
```

由于 Scout 搜索返回 Eloquent 模型集合，你甚至可以直接从路由或控制器返回结果，它们会自动转换为 JSON：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/search', function (Request $request) {
    return Order::search($request->search)->get();
});
```

如果要在搜索结果转换为 Eloquent 模型之前获取原始结果，可以使用 `raw` 方法：

```php
$orders = Order::search('Star Trek')->raw();
```

<a name="semantic-search"></a>
### 语义搜索

数据库、Meilisearch、Typesense 和 Turbopuffer 引擎支持语义搜索，即根据查询的含义匹配记录。当 Scout 生成嵌入向量时，语义搜索和混合搜索需要 [Laravel AI SDK](/docs/{{version}}/ai-sdk)。[Typesense 原生嵌入](#typesense-embeddings)、[Turbopuffer 原生嵌入](#turbopuffer-configuration) 和预先计算的查询向量则不需要 Laravel AI SDK。

为选定引擎配置嵌入后，在搜索查询上调用 `semantic` 方法：

```php
$articles = Article::search('staying cool in the summer')
    ->semantic()
    ->get();
```

当选定引擎支持时，你可以提供最低相似度阈值：

```php
$articles = Article::search('renewable energy storage')
    ->semantic(minSimilarity: 0.6)
    ->get();
```

要结合全文搜索和语义搜索，请使用 `hybrid` 方法。其前两个参数控制文本结果和语义结果的相对权重：

```php
$articles = Article::search('renewable energy storage')
    ->hybrid(textWeight: 1, semanticWeight: 2)
    ->get();
```

<a name="custom-indexes"></a>
#### 自定义索引

使用第三方引擎搜索时，搜索查询通常针对模型的 [searchableAs](#configuring-model-indexes) 方法指定的索引执行。不过，可以使用 `within` 方法指定要搜索的自定义索引：

```php
$orders = Order::search('Star Trek')
    ->within('tv_shows_popularity_desc')
    ->get();
```

<a name="where-clauses"></a>
### Where 子句

Scout 允许为搜索查询添加「where」子句。例如，基本的相等性检查可用于按所有者 ID 限定搜索查询范围：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->where('user_id', 1)->get();
```

你也可以使用 `=`、`!=`、`<`、`>`、`>=`、`<=` 比较运算符构建更高级的查询：

```php
Order::search('Star Trek')
  ->where('status', '=', 'completed')
  ->where('is_refunded', '!=', true)
  ->where('total_price', '>', 100)
  ->where('shipping_cost', '<', 20)
  ->where('discount_percent', '>=', 10)
  ->where('item_count', '<=', 5)
  ->get();
```

此外，可以使用 `whereIn` 方法验证给定列的值是否包含在给定数组中：

```php
$orders = Order::search('Star Trek')->whereIn(
    'status', ['open', 'paid']
)->get();
```

`whereNotIn` 方法验证给定列的值是否不包含在给定数组中：

```php
$orders = Order::search('Star Trek')->whereNotIn(
    'status', ['closed']
)->get();
```

> [!WARNING]
> 如果应用使用 Meilisearch，必须先配置应用的 [可筛选属性](#meilisearch-index-settings)，然后才能使用 Scout 的「where」子句。

<a name="customizing-the-eloquent-results-query"></a>
#### 自定义 Eloquent 结果查询

Scout 从应用的搜索引擎检索到匹配的 Eloquent 模型列表后，会使用 Eloquent 根据主键检索所有匹配的模型。你可以调用 `query` 方法自定义此查询。`query` 方法接受一个闭包，该闭包会接收 Eloquent 查询构建器实例作为参数：

```php
use App\Models\Order;
use Illuminate\Database\Eloquent\Builder;

$orders = Order::search('Star Trek')
    ->query(fn (Builder $query) => $query->with('invoices'))
    ->get();
```

使用第三方引擎时，此回调在相关模型已从搜索引擎中检索出来之后调用，因此不应用它来「筛选」结果，而应使用 [Scout where 子句](#where-clauses)。不过，使用数据库引擎时，`query` 方法的约束会直接应用于数据库查询，因此也可以用它进行筛选。

<a name="pagination"></a>
### 分页

除了获取模型集合外，还可以使用 `paginate` 方法对搜索结果分页。与 [对普通 Eloquent 查询分页](/docs/{{version}}/pagination) 一样，该方法会返回一个 `Illuminate\Pagination\LengthAwarePaginator` 实例：

```php
use App\Models\Order;

$orders = Order::search('Star Trek')->paginate();
```

可以将数量作为第一个参数传给 `paginate` 方法，指定每页获取的模型数量：

```php
$orders = Order::search('Star Trek')->paginate(15);
```

使用数据库引擎时，还可以使用 `simplePaginate` 方法。与获取匹配记录总数以显示页码的 `paginate` 不同，`simplePaginate` 只判断当前页之后是否还有更多结果。因此，对于只需要「上一页」和「下一页」链接的大型数据集，它更高效：

```php
$orders = Order::search('Star Trek')->simplePaginate(15);
```

获取结果后，可以使用 [Blade](/docs/{{version}}/blade) 显示结果并渲染分页链接，就像对普通 Eloquent 查询分页一样：

```html
<div class="container">
    @foreach ($orders as $order)
        {{ $order->price }}
    @endforeach
</div>

{{ $orders->links() }}
```

当然，如果想以 JSON 格式获取分页结果，可以直接从路由或控制器返回分页器实例：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/orders', function (Request $request) {
    return Order::search($request->input('query'))->paginate(15);
});
```

> [!WARNING]
> 由于搜索引擎不了解 Eloquent 模型的全局作用域定义，因此在使用 Scout 分页的应用中不应使用全局作用域。或者，你应该在通过 Scout 搜索时重新应用全局作用域的约束。

<a name="soft-deleting"></a>
### 软删除

如果索引中的模型使用 [软删除](/docs/{{version}}/eloquent#soft-deleting)，且需要搜索软删除的模型，请将 `config/scout.php` 配置文件的 `soft_delete` 选项设为 `true`：

```php
'soft_delete' => true,
```

当此配置选项为 `true` 时，Scout 不会从搜索索引中移除软删除的模型，而是在索引记录上设置一个隐藏的 `__soft_deleted` 属性。然后，你可以在搜索时使用 `withTrashed` 或 `onlyTrashed` 方法检索软删除的记录：

```php
use App\Models\Order;

// 检索结果时包含已删除的记录……
$orders = Order::search('Star Trek')->withTrashed()->get();

// 检索结果时仅包含已删除的记录……
$orders = Order::search('Star Trek')->onlyTrashed()->get();
```

> [!NOTE]
> 使用 `forceDelete` 永久删除软删除的模型时，Scout 会自动将其从搜索索引中移除。

<a name="customizing-engine-searches"></a>
### 自定义引擎搜索

如果需要对引擎的搜索行为进行高级自定义，可以将闭包作为第二个参数传递给 `search` 方法。例如，可以使用此回调在搜索查询传给 Algolia 之前，将地理位置数据添加到搜索选项中：

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

<a name="custom-engines"></a>
## 自定义引擎

<a name="writing-the-engine"></a>
#### 编写引擎

如果 Scout 内置的搜索引擎不符合你的需求，可以编写自己的自定义引擎并将其注册到 Scout。引擎应继承 `Laravel\Scout\Engines\Engine` 抽象类。该抽象类包含自定义引擎必须实现的八个方法：

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

查看 `Laravel\Scout\Engines\AlgoliaEngine` 类中这些方法的实现可能会有所帮助。该类为学习如何在自定义引擎中实现这些方法提供了很好的起点。

<a name="registering-the-engine"></a>
#### 注册引擎

编写自定义引擎后，可以使用 Scout 引擎管理器的 `extend` 方法将其注册到 Scout。Scout 引擎管理器可以从 Laravel 服务容器解析。应在 `App\Providers\AppServiceProvider` 类或应用使用的其他服务提供者的 `boot` 方法中调用 `extend` 方法：

```php
use App\ScoutExtensions\MySqlSearchEngine;
use Laravel\Scout\EngineManager;

/**
 * 启动所有应用服务。
 */
public function boot(): void
{
    resolve(EngineManager::class)->extend('mysql', function () {
        return new MySqlSearchEngine;
    });
}
```

注册引擎后，可以在应用的 `config/scout.php` 配置文件中将其指定为默认的 Scout `driver`：

```php
'driver' => 'mysql',
```
