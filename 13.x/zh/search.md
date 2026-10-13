# 搜索

- [简介](#introduction)
    - [全文搜索](#introduction-full-text-search)
    - [语义搜索 / 向量搜索](#introduction-semantic-vector-search)
    - [重排序](#introduction-reranking)
    - [Scout 搜索引擎](#introduction-scout-search-engines)
- [全文搜索](#full-text-search)
    - [添加全文索引](#adding-full-text-indexes)
    - [执行全文查询](#running-full-text-queries)
- [语义搜索 / 向量搜索](#semantic-vector-search)
    - [生成嵌入向量](#generating-embeddings)
    - [存储向量与建立索引](#storing-and-indexing-vectors)
    - [按相似度查询](#querying-by-similarity)
- [对结果进行重排序](#reranking-results)
- [Laravel Scout](#laravel-scout)
    - [数据库引擎](#database-engine)
    - [第三方引擎](#third-party-engines)
- [组合使用搜索技术](#combining-techniques)

<a name="introduction"></a>
## 简介

几乎所有应用程序都需要搜索功能。无论用户是在知识库中查找相关文章、浏览商品目录，还是针对一组文档用自然语言提问，Laravel 都提供了适用于这些场景的内置工具，而且通常无需借助任何外部服务。

对于大多数应用程序，Laravel 内置的基于数据库的搜索方案已经足够。只有需要大规模的拼写容错、分面筛选或地理位置搜索等功能时，才需要外部搜索服务。

<a name="introduction-full-text-search"></a>
#### 全文搜索

如果你需要按关键词相关性排序，即由数据库根据结果与搜索词的匹配程度进行评分和排序，可以使用 Laravel 查询构造器的 `whereFullText` 方法，它利用 MariaDB、MySQL 和 PostgreSQL 的原生全文索引。全文搜索能够识别单词边界并进行词干提取，因此搜索「running」可以匹配包含「run」的记录。整个过程无需外部服务。

<a name="introduction-semantic-vector-search"></a>
#### 语义搜索 / 向量搜索

对于由 AI 驱动、依据 *含义* 而非精确关键词匹配结果的语义搜索，查询构造器的 `whereVectorSimilarTo` 方法会使用存储在启用了 `pgvector` 扩展的 PostgreSQL 或 MariaDB 中的嵌入向量。例如，搜索「纳帕谷最好的酒庄」可以找到标题为「最值得参观的葡萄园」的文章，即使二者没有相同的词语。向量搜索需要启用了 `pgvector` 扩展的 PostgreSQL 或 MariaDB 11.7 及以上版本，以及 [Laravel AI SDK](/docs/{{version}}/ai-sdk)。

<a name="introduction-reranking"></a>
#### 重排序

Laravel 的 [AI SDK](/docs/{{version}}/ai-sdk) 提供重排序功能，利用 AI 模型根据结果与查询的语义相关性，对任意一组结果重新排序。在全文搜索等快速初步检索之后，将重排序作为第二阶段尤其有效，可以兼顾速度与语义准确性。

<a name="introduction-scout-search-engines"></a>
#### Laravel Scout 搜索

如果你的应用程序希望通过 `Searchable` trait 自动保持搜索索引与 Eloquent 模型同步，[Laravel Scout](/docs/{{version}}/scout) 既提供内置数据库引擎，也提供适用于 Algolia、Meilisearch、Typesense 和 Turbopuffer 等第三方服务的驱动。

<a name="full-text-search"></a>
## 全文搜索

`LIKE` 查询适合简单的子字符串匹配，但无法理解语言。使用 `LIKE` 搜索「running」不会找到包含「run」的记录，结果也不会按相关性排序，而是按照数据库找到它们的顺序返回。全文搜索通过专门的索引解决了这两个问题：索引支持单词边界识别、词干提取和相关性评分，让数据库优先返回最相关的结果。

MariaDB、MySQL 和 PostgreSQL 都内置了快速全文搜索功能，无需外部搜索服务。你只需为要搜索的列添加全文索引，然后使用查询构造器的 `whereFullText` 方法进行搜索。

> [!WARNING]
> 目前 MariaDB、MySQL 和 PostgreSQL 支持全文搜索。

<a name="adding-full-text-indexes"></a>
### 添加全文索引

使用全文搜索之前，首先要为需要搜索的列添加全文索引。你可以为单列添加索引，也可以传入列名数组来创建复合索引，从而同时搜索多个字段：

```php
Schema::create('articles', function (Blueprint $table) {
    $table->id();
    $table->string('title');
    $table->text('body');
    $table->timestamps();

    $table->fullText(['title', 'body']);
});
```

在 PostgreSQL 中，你可以为索引指定语言配置，以控制词干提取的方式：

```php
$table->fullText('body')->language('english');
```

有关创建索引的更多信息，请参阅 [迁移文档](/docs/{{version}}/migrations#available-index-types)。

<a name="running-full-text-queries"></a>
### 执行全文查询

建立索引后，使用查询构造器的 `whereFullText` 方法进行搜索。Laravel 会根据数据库驱动生成相应的 SQL，例如在 MariaDB 和 MySQL 中使用 `MATCH(...) AGAINST(...)`，在 PostgreSQL 中使用 `to_tsvector(...) @@ plainto_tsquery(...)`：

```php
$articles = Article::whereFullText('body', 'web developer')->get();
```

使用 MariaDB 和 MySQL 时，结果会自动按相关性评分排序。在 PostgreSQL 中，`whereFullText` 会筛选出匹配的记录，但不会按相关性排序。如果你需要在 PostgreSQL 中自动按相关性排序，可以考虑使用 [Scout 的数据库引擎](#database-engine)，它会替你完成排序。

如果你为多个列创建了复合全文索引，可以向 `whereFullText` 传入相同的列名数组，同时搜索这些列：

```php
$articles = Article::whereFullText(
    ['title', 'body'], 'web developer'
)->get();
```

你可以使用 `orWhereFullText` 方法，以「或」条件添加全文搜索子句。完整说明请参阅 [查询构造器文档](/docs/{{version}}/queries#full-text-where-clauses)。

<a name="semantic-vector-search"></a>
## 语义搜索 / 向量搜索

全文搜索依赖关键词匹配，查询中的词语必须以某种形式出现在数据中。语义搜索采用了根本不同的方式：使用 AI 生成的嵌入向量，将文本的 *含义* 表示为数字数组，再查找含义与查询最相近的结果。例如，搜索「纳帕谷最好的酒庄」可以找到标题为「最值得参观的葡萄园」的文章，即使二者完全没有相同的词语。

向量搜索的基本流程是：为每条内容生成一个嵌入向量（数字数组），并将其与数据一起存储；搜索时，为用户的查询生成嵌入向量，再从已存储的向量中找到在向量空间里与它最接近的向量。

> [!NOTE]
> 向量搜索需要 [Laravel AI SDK](/docs/{{version}}/ai-sdk)，并支持 PostgreSQL（需要 `pgvector` 扩展）、MariaDB 11.7 及以上版本和 MongoDB（需要 [Laravel MongoDB 扩展包](https://laravel.com/docs/13.x/mongodb)）。[Laravel Cloud](https://laravel.com/cloud) 上的所有 Postgres 数据库都已安装 `pgvector`。

<a name="generating-embeddings"></a>
### 生成嵌入向量

嵌入向量是一个高维数字数组，通常包含数百或数千个数字，用于表示一段文本的语义。你可以使用 Laravel 的 `Stringable` 类提供的 `toEmbeddings` 方法，为字符串生成嵌入向量：

```php
use Illuminate\Support\Str;

$embedding = Str::of('Napa Valley has great wine.')->toEmbeddings();
```

要一次为多个输入生成嵌入向量，可以使用 `Embeddings` 类。由于只需向嵌入模型提供商发起一次 API 调用，这比逐个生成向量更高效：

```php
use Laravel\Ai\Embeddings;

$response = Embeddings::for([
    'Napa Valley has great wine.',
    'Laravel is a PHP framework.',
])->generate();

$response->embeddings; // [[0.123, 0.456, ...], [0.789, 0.012, ...]]
```

有关配置嵌入模型提供商、自定义维度和缓存的更多信息，请参阅 [AI SDK 文档](/docs/{{version}}/ai-sdk#embeddings)。

<a name="storing-and-indexing-vectors"></a>
### 存储向量与建立索引

要存储嵌入向量，请在迁移中定义一个 `vector` 列，并指定与嵌入模型提供商输出一致的维度数（例如，OpenAI 的 `text-embedding-3-small` 模型对应 1536 维）。你还应在该列上调用 `index`，创建 HNSW（Hierarchical Navigable Small World，分层可导航小世界）索引，以显著加快大型数据集上的相似度搜索：

```php
Schema::ensureVectorExtensionExists();

Schema::create('documents', function (Blueprint $table) {
    $table->id();
    $table->string('title');
    $table->text('content');
    $table->vector('embedding', dimensions: 1536)->index();
    $table->timestamps();
});
```

`Schema::ensureVectorExtensionExists` 方法会确保在创建表之前，你的 PostgreSQL 数据库已启用 `pgvector` 扩展。

在 Eloquent 模型中，使用 `AsVector` 类型转换，让 Laravel 自动处理 PHP 数组与数据库向量格式之间的转换：

```php
use Illuminate\Database\Eloquent\Casts\AsVector;

protected function casts(): array
{
    return [
        'embedding' => AsVector::class,
    ];
}
```

有关向量列和索引的更多信息，请参阅 [迁移文档](/docs/{{version}}/migrations#available-column-types)。

<a name="querying-by-similarity"></a>
### 按相似度查询

存储内容的嵌入向量后，你可以使用 `whereVectorSimilarTo` 方法搜索相似记录。该方法通过余弦相似度比较给定的嵌入向量与已存储的向量，过滤掉低于 `minSimilarity` 阈值的结果，并自动按相关性排序，将最相似的记录排在最前面。阈值应在 `0.0` 到 `1.0` 之间，其中 `1.0` 表示向量完全相同：

```php
$documents = Document::query()
    ->whereVectorSimilarTo('embedding', $queryEmbedding, minSimilarity: 0.4)
    ->limit(10)
    ->get();
```

为方便使用，当你传入普通字符串而非嵌入向量数组时，Laravel 会使用已配置的嵌入模型提供商自动生成向量。因此，你可以直接传入用户的搜索查询，无需先手动将其转换为嵌入向量：

```php
$documents = Document::query()
    ->whereVectorSimilarTo('embedding', 'best wineries in Napa Valley')
    ->limit(10)
    ->get();
```

如果需要更底层地控制向量查询，还可以使用 `whereVectorDistanceLessThan`、`selectVectorDistance` 和 `orderByVectorDistance` 方法。这些方法允许你直接使用距离值而非相似度评分，将计算出的距离作为结果中的一列，或手动控制排序。完整说明请参阅 [查询构造器文档](/docs/{{version}}/queries#vector-similarity-clauses) 和 [AI SDK 文档](/docs/{{version}}/ai-sdk#querying-embeddings)。

<a name="reranking-results"></a>
## 对结果进行重排序

重排序是一种利用 AI 模型，根据每个结果与给定查询的语义相关性，对一组结果重新排序的技术。向量搜索需要预先计算并存储嵌入向量，而重排序适用于任意一组文本：它接收原始内容和查询，返回按相关性排序的条目。

在快速初步检索之后，将重排序作为第二阶段尤其有效。例如，你可以先使用全文搜索，从数千条记录中快速筛出前 50 条候选结果，再通过重排序将最相关的结果排在最前面。这种「先检索，再重排序」的模式兼顾了速度与语义准确性。

你可以使用 `Reranking` 类对字符串数组进行重排序：

```php
use Laravel\Ai\Reranking;

$response = Reranking::of([
    'Django is a Python web framework.',
    'Laravel is a PHP web application framework.',
    'React is a JavaScript library for building user interfaces.',
])->rerank('PHP frameworks');

$response->first()->document; // "Laravel is a PHP web application framework."
```

Laravel 集合还提供了 `rerank` 宏，它接受字段名（或闭包）和查询，方便你对 Eloquent 结果进行重排序：

```php
$articles = Article::all()
    ->rerank('body', 'Laravel tutorials');
```

有关配置重排序模型提供商和可用选项的完整说明，请参阅 [AI SDK 文档](/docs/{{version}}/ai-sdk#reranking)。

<a name="laravel-scout"></a>
## Laravel Scout

上述搜索技术都通过在代码中直接调用查询构造器方法来使用。[Laravel Scout](/docs/{{version}}/scout) 则采用另一种方式：它提供 `Searchable` trait，你只需将其添加到 Eloquent 模型中，Scout 就会在记录创建、更新和删除时自动同步搜索索引。如果你希望模型始终可以被搜索，又不想手动管理索引更新，这种方式尤其方便。

<a name="database-engine"></a>
### 数据库引擎

Scout 的内置数据库引擎会在现有数据库中执行全文搜索和 `LIKE` 搜索，无需外部服务或额外的基础设施。你只需为模型添加 `Searchable` trait，并定义 `toSearchableArray` 方法，返回希望用于搜索的列。

你可以使用 PHP 属性（Attribute）来控制每列的搜索策略。`SearchUsingFullText` 会使用数据库的全文索引，`SearchUsingPrefix` 只从字符串开头匹配（`example%`），未指定属性的列则使用默认的 `LIKE` 策略，在搜索词两侧添加通配符（`%example%`）：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Attributes\SearchUsingFullText;
use Laravel\Scout\Attributes\SearchUsingPrefix;
use Laravel\Scout\Searchable;

class Article extends Model
{
    use Searchable;

    #[SearchUsingPrefix(['id'])]
    #[SearchUsingFullText(['title', 'body'])]
    public function toSearchableArray(): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'body' => $this->body,
        ];
    }
}
```

> [!WARNING]
> 在指定某列使用全文查询条件之前，请确保该列已建立 [全文索引](/docs/{{version}}/migrations#available-index-types)。

添加 trait 后，你就可以使用 Scout 的 `search` 方法搜索模型。Scout 的数据库引擎会自动按相关性排序结果，即使在 PostgreSQL 中也是如此：

```php
$articles = Article::search('Laravel')->get();
```

如果你的搜索需求适中，希望享受 Scout 自动同步索引的便利，又不想部署外部服务，数据库引擎是一个很好的选择。它能很好地处理大多数常见的搜索场景，包括筛选、分页和软删除记录处理。完整说明请参阅 [Scout 文档](/docs/{{version}}/scout#database-engine)。

<a name="third-party-engines"></a>
### 第三方引擎

Scout 还支持 [Algolia](https://www.algolia.com/)、[Meilisearch](https://www.meilisearch.com) 和 [Typesense](https://typesense.org) 等第三方搜索引擎。这些专门的搜索服务提供拼写容错、分面筛选、地理位置搜索和自定义排序规则等高级功能。当数据规模非常大，或需要出色的即时搜索体验时，这些功能就十分重要。

由于 Scout 为所有驱动提供统一的 API，后续从数据库引擎切换到第三方引擎只需极少的代码改动。你可以先使用数据库引擎，只有在应用程序的需求超出数据库所能提供的能力时，再迁移到第三方服务。

有关配置第三方引擎的完整说明，请参阅 [Scout 文档](/docs/{{version}}/scout)。

> [!NOTE]
> 许多应用程序始终无需外部搜索引擎。本页介绍的内置搜索技术已覆盖绝大多数使用场景。

<a name="combining-techniques"></a>
## 组合使用搜索技术

本页介绍的搜索技术可以配合使用，组合起来往往能取得最佳效果。以下两种常见模式展示了如何搭配这些工具。

**全文检索 + 重排序**

使用全文搜索，从大型数据集中快速筛出一组候选结果，再通过重排序按语义相关性对这些结果排序。这样既能利用数据库原生全文搜索的速度，又能获得 AI 相关性评分的准确性：

```php
$articles = Article::query()
    ->whereFullText('body', $request->input('query'))
    ->limit(50)
    ->get()
    ->rerank('body', $request->input('query'), limit: 10);
```

**向量搜索 + 传统筛选条件**

将向量相似度查询与标准的 `where` 子句结合，可以将语义搜索限定在部分记录内。当你希望依据含义搜索，又需要按归属、分类或其他属性限制结果时，这种方式很有用：

```php
$documents = Document::query()
    ->where('team_id', $user->team_id)
    ->whereVectorSimilarTo('embedding', $request->input('query'))
    ->limit(10)
    ->get();
```
