
# 字符串

- [介绍](#introduction)
- [可用的方法](#available-methods)

<a name="introduction"></a>
## 介绍

Laravel 提供了多种用于操作`字符串值`的函数。其中许多函数被框架自身使用；不过，如果你觉得方便，也可以在自己的应用中使用它们。

<a name="available-methods"></a>
## 可用的方法

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

<a name="strings-method-list"></a>
### 字符串

<div class="collection-method-list" markdown="1">

[\__](#method-__)
[class_basename](#method-class-basename)
[e](#method-e)
[preg_replace_array](#method-preg-replace-array)
[Str::after](#method-str-after)
[Str::afterLast](#method-str-after-last)
[Str::apa](#method-str-apa)
[Str::ascii](#method-str-ascii)
[Str::before](#method-str-before)
[Str::beforeLast](#method-str-before-last)
[Str::between](#method-str-between)
[Str::betweenFirst](#method-str-between-first)
[Str::camel](#method-camel-case)
[Str::charAt](#method-char-at)
[Str::chopStart](#method-str-chop-start)
[Str::chopEnd](#method-str-chop-end)
[Str::contains](#method-str-contains)
[Str::containsAll](#method-str-contains-all)
[Str::doesntContain](#method-str-doesnt-contain)
[Str::deduplicate](#method-deduplicate)
[Str::endsWith](#method-ends-with)
[Str::excerpt](#method-excerpt)
[Str::finish](#method-str-finish)
[Str::headline](#method-str-headline)
[Str::inlineMarkdown](#method-str-inline-markdown)
[Str::is](#method-str-is)
[Str::isAscii](#method-str-is-ascii)
[Str::isJson](#method-str-is-json)
[Str::isUlid](#method-str-is-ulid)
[Str::isUrl](#method-str-is-url)
[Str::isUuid](#method-str-is-uuid)
[Str::kebab](#method-kebab-case)
[Str::lcfirst](#method-str-lcfirst)
[Str::length](#method-str-length)
[Str::limit](#method-str-limit)
[Str::lower](#method-str-lower)
[Str::markdown](#method-str-markdown)
[Str::mask](#method-str-mask)
[Str::orderedUuid](#method-str-ordered-uuid)
[Str::padBoth](#method-str-padboth)
[Str::padLeft](#method-str-padleft)
[Str::padRight](#method-str-padright)
[Str::password](#method-str-password)
[Str::plural](#method-str-plural)
[Str::pluralStudly](#method-str-plural-studly)
[Str::position](#method-str-position)
[Str::random](#method-str-random)
[Str::remove](#method-str-remove)
[Str::repeat](#method-str-repeat)
[Str::replace](#method-str-replace)
[Str::replaceArray](#method-str-replace-array)
[Str::replaceFirst](#method-str-replace-first)
[Str::replaceLast](#method-str-replace-last)
[Str::replaceMatches](#method-str-replace-matches)
[Str::replaceStart](#method-str-replace-start)
[Str::replaceEnd](#method-str-replace-end)
[Str::reverse](#method-str-reverse)
[Str::singular](#method-str-singular)
[Str::slug](#method-str-slug)
[Str::snake](#method-snake-case)
[Str::squish](#method-str-squish)
[Str::start](#method-str-start)
[Str::startsWith](#method-starts-with)
[Str::studly](#method-studly-case)
[Str::substr](#method-str-substr)
[Str::substrCount](#method-str-substrcount)
[Str::substrReplace](#method-str-substrreplace)
[Str::swap](#method-str-swap)
[Str::take](#method-take)
[Str::title](#method-title-case)
[Str::toBase64](#method-str-to-base64)
[Str::transliterate](#method-str-transliterate)
[Str::trim](#method-str-trim)
[Str::ltrim](#method-str-ltrim)
[Str::rtrim](#method-str-rtrim)
[Str::ucfirst](#method-str-ucfirst)
[Str::ucsplit](#method-str-ucsplit)
[Str::upper](#method-str-upper)
[Str::ulid](#method-str-ulid)
[Str::unwrap](#method-str-unwrap)
[Str::uuid](#method-str-uuid)
[Str::uuid7](#method-str-uuid7)
[Str::wordCount](#method-str-word-count)
[Str::wordWrap](#method-str-word-wrap)
[Str::words](#method-str-words)
[Str::wrap](#method-str-wrap)
[str](#method-str)
[trans](#method-trans)
[trans_choice](#method-trans-choice)

</div>



### Fluent Strings （流式字符串）

[after](#method-fluent-str-after)
[afterLast](#method-fluent-str-after-last)
[apa](#method-fluent-str-apa)
[append](#method-fluent-str-append)
[ascii](#method-fluent-str-ascii)
[basename](#method-fluent-str-basename)
[before](#method-fluent-str-before)
[beforeLast](#method-fluent-str-before-last)
[between](#method-fluent-str-between)
[betweenFirst](#method-fluent-str-between-first)
[camel](#method-fluent-str-camel)
[charAt](#method-fluent-str-char-at)
[classBasename](#method-fluent-str-class-basename)
[chopStart](#method-fluent-str-chop-start)
[chopEnd](#method-fluent-str-chop-end)
[contains](#method-fluent-str-contains)
[containsAll](#method-fluent-str-contains-all)
[deduplicate](#method-fluent-str-deduplicate)
[dirname](#method-fluent-str-dirname)
[endsWith](#method-fluent-str-ends-with)
[exactly](#method-fluent-str-exactly)
[excerpt](#method-fluent-str-excerpt)
[explode](#method-fluent-str-explode)
[finish](#method-fluent-str-finish)
[headline](#method-fluent-str-headline)
[inlineMarkdown](#method-fluent-str-inline-markdown)
[is](#method-fluent-str-is)
[isAscii](#method-fluent-str-is-ascii)
[isEmpty](#method-fluent-str-is-empty)
[isNotEmpty](#method-fluent-str-is-not-empty)
[isJson](#method-fluent-str-is-json)
[isUlid](#method-fluent-str-is-ulid)
[isUrl](#method-fluent-str-is-url)
[isUuid](#method-fluent-str-is-uuid)
[kebab](#method-fluent-str-kebab)
[lcfirst](#method-fluent-str-lcfirst)
[length](#method-fluent-str-length)
[limit](#method-fluent-str-limit)
[lower](#method-fluent-str-lower)
[markdown](#method-fluent-str-markdown)
[mask](#method-fluent-str-mask)
[match](#method-fluent-str-match)
[matchAll](#method-fluent-str-match-all)
[isMatch](#method-fluent-str-is-match)
[newLine](#method-fluent-str-new-line)
[padBoth](#method-fluent-str-padboth)
[padLeft](#method-fluent-str-padleft)
[padRight](#method-fluent-str-padright)
[pipe](#method-fluent-str-pipe)
[plural](#method-fluent-str-plural)
[position](#method-fluent-str-position)
[prepend](#method-fluent-str-prepend)
[remove](#method-fluent-str-remove)
[repeat](#method-fluent-str-repeat)
[replace](#method-fluent-str-replace)
[replaceArray](#method-fluent-str-replace-array)
[replaceFirst](#method-fluent-str-replace-first)
[replaceLast](#method-fluent-str-replace-last)
[replaceMatches](#method-fluent-str-replace-matches)
[replaceStart](#method-fluent-str-replace-start)
[replaceEnd](#method-fluent-str-replace-end)
[scan](#method-fluent-str-scan)
[singular](#method-fluent-str-singular)
[slug](#method-fluent-str-slug)
[snake](#method-fluent-str-snake)
[split](#method-fluent-str-split)
[squish](#method-fluent-str-squish)
[start](#method-fluent-str-start)
[startsWith](#method-fluent-str-starts-with)
[stripTags](#method-fluent-str-strip-tags)
[studly](#method-fluent-str-studly)
[substr](#method-fluent-str-substr)
[substrReplace](#method-fluent-str-substrreplace)
[swap](#method-fluent-str-swap)
[take](#method-fluent-str-take)
[tap](#method-fluent-str-tap)
[test](#method-fluent-str-test)
[title](#method-fluent-str-title)
[toBase64](#method-fluent-str-to-base64)
[toHtmlString](#method-fluent-str-to-html-string)
[toUri](#method-fluent-str-to-uri)
[transliterate](#method-fluent-str-transliterate)
[trim](#method-fluent-str-trim)
[ltrim](#method-fluent-str-ltrim)
[rtrim](#method-fluent-str-rtrim)
[ucfirst](#method-fluent-str-ucfirst)
[ucsplit](#method-fluent-str-ucsplit)
[unwrap](#method-fluent-str-unwrap)
[upper](#method-fluent-str-upper)
[when](#method-fluent-str-when)
[whenContains](#method-fluent-str-when-contains)
[whenContainsAll](#method-fluent-str-when-contains-all)
[whenEmpty](#method-fluent-str-when-empty)
[whenNotEmpty](#method-fluent-str-when-not-empty)
[whenStartsWith](#method-fluent-str-when-starts-with)
[whenEndsWith](#method-fluent-str-when-ends-with)
[whenExactly](#method-fluent-str-when-exactly)
[whenNotExactly](#method-fluent-str-when-not-exactly)
[whenIs](#method-fluent-str-when-is)
[whenIsAscii](#method-fluent-str-when-is-ascii)
[whenIsUlid](#method-fluent-str-when-is-ulid)
[whenIsUuid](#method-fluent-str-when-is-uuid)
[whenTest](#method-fluent-str-when-test)
[wordCount](#method-fluent-str-word-count)
[words](#method-fluent-str-words)
[wrap](#method-fluent-str-wrap)

</div>
<a name="strings"></a>

## Strings （字符串）
<a name="method-__"></a>
#### `__()` {.collection-method}

`__` 函数会使用你的 [语言文件](/docs/laravel/12.x/localization) 翻译给定的翻译字符串或翻译键：

```php
echo __('Welcome to our application');

echo __('messages.welcome');
```



如果指定的翻译字符串或键不存在，`__` 函数将返回给定的值。因此，使用上面的示例，如果该翻译键不存在，`__` 函数将返回 `messages.welcome`。

<a name="method-class-basename"></a>
#### `class_basename()` {.collection-method}

`class_basename` 函数返回给定类的类名，并移除类的命名空间：

```php
$class = class_basename('Foo\Bar\Baz');

// Baz
```

<a name="method-e"></a>
#### `e()` {.collection-method}

`e` 函数运行 PHP 的 `htmlspecialchars` 函数，默认将 `double_encode` 选项设置为 `true`：

```php
echo e('<html>foo</html>');

// &lt;html&gt;foo&lt;/html&gt;
```

<a name="method-preg-replace-array"></a>
#### `preg_replace_array()` {.collection-method}

`preg_replace_array` 函数使用数组按顺序替换字符串中的给定模式：

```php
$string = 'The event will take place between :start and :end';

$replaced = preg_replace_array('/:[a-z_]+/', ['8:30', '9:00'], $string);

// The event will take place between 8:30 and 9:00
```

<a name="method-str-after"></a>
#### `Str::after()` {.collection-method}

`Str::after` 方法返回字符串中给定值之后的所有内容。如果值在字符串中不存在，则返回整个字符串：

```php
use Illuminate\Support\Str;

$slice = Str::after('This is my name', 'This is');

// ' my name'
```

<a name="method-str-after-last"></a>
#### `Str::afterLast()` {.collection-method}

`Str::afterLast` 方法返回字符串中给定值最后一次出现之后的所有内容。如果值在字符串中不存在，则返回整个字符串：

```php
use Illuminate\Support\Str;

$slice = Str::afterLast('App\Http\Controllers\Controller', '\\');

// 'Controller'
```



#### `Str::apa()` {.collection-method}

`Str::apa` 方法会将给定字符串转换为 **标题格式 (title case)**，
遵循 [APA 指南](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case)：

```php
use Illuminate\Support\Str;

$title = Str::apa('Creating A Project');

// 'Creating a Project'
```

#### `Str::ascii()` {.collection-method}

`Str::ascii` 方法会尝试将字符串 **音译为 ASCII 值**：

```php
use Illuminate\Support\Str;

$slice = Str::ascii('û');

// 'u'
```

#### `Str::before()` {.collection-method}

`Str::before` 方法返回字符串中 **指定值之前的所有内容**：

```php
use Illuminate\Support\Str;

$slice = Str::before('This is my name', 'my name');

// 'This is '
```

#### `Str::beforeLast()` {.collection-method}

`Str::beforeLast` 方法返回字符串中 **最后一次出现指定值之前的所有内容**：

```php
use Illuminate\Support\Str;

$slice = Str::beforeLast('This is my name', 'is');

// 'This '
```

#### `Str::between()` {.collection-method}

`Str::between` 方法返回字符串中 **两个值之间的部分内容**：

```php
use Illuminate\Support\Str;

$slice = Str::between('This is my name', 'This', 'name');

// ' is my '
```

#### `Str::betweenFirst()` {.collection-method}

`Str::betweenFirst` 方法返回字符串中 **两个值之间最小可能的部分内容**：

```php
use Illuminate\Support\Str;

$slice = Str::betweenFirst('[a] bc [d]', '[', ']');

// 'a'
```

#### `Str::camel()` {.collection-method}

`Str::camel` 方法会将给定字符串转换为 **camelCase 格式**：

```php
use Illuminate\Support\Str;

$converted = Str::camel('foo_bar');

// 'fooBar'
```



#### `Str::charAt()` {.collection-method}

`Str::charAt` 方法返回指定索引处的字符。如果索引超出范围，则返回 `false`：

```php
use Illuminate\Support\Str;

$character = Str::charAt('This is my name.', 6);

// 's'
```

#### `Str::chopStart()` {.collection-method}

`Str::chopStart` 方法会移除字符串开头第一次出现的给定值，前提是该值确实出现在字符串的开头：

```php
use Illuminate\Support\Str;

$url = Str::chopStart('https://laravel.com', 'https://');

// 'laravel.com'
```

你也可以将数组作为第二个参数传入。
如果字符串是以数组中的任意一个值开头，那么该值会被移除：

```php
use Illuminate\Support\Str;

$url = Str::chopStart('http://laravel.com', ['https://', 'http://']);

// 'laravel.com'
```

#### `Str::chopEnd()` {.collection-method}

`Str::chopEnd` 方法会移除字符串结尾最后一次出现的给定值，前提是该值确实出现在字符串的结尾：

```php
use Illuminate\Support\Str;

$url = Str::chopEnd('app/Models/Photograph.php', '.php');

// 'app/Models/Photograph'
```

你也可以将数组作为第二个参数传入。
如果字符串是以数组中的任意一个值结尾，那么该值会被移除：

```php
use Illuminate\Support\Str;

$url = Str::chopEnd('laravel.com/index.php', ['/index.html', '/index.php']);

// 'laravel.com'
```

#### `Str::contains()` {.collection-method}

`Str::contains` 方法用于判断给定字符串是否包含指定的值。
默认情况下，该方法区分大小写：

```php
use Illuminate\Support\Str;

$contains = Str::contains('This is my name', 'my');

// true
```



你也可以传递一个值数组，用来判断给定字符串是否包含数组中的任意值：

```php
use Illuminate\Support\Str;

$contains = Str::contains('This is my name', ['my', 'foo']);

// true
```

你可以通过将 `ignoreCase` 参数设置为 `true` 来禁用大小写敏感：

```php
use Illuminate\Support\Str;

$contains = Str::contains('This is my name', 'MY', ignoreCase: true);

// true
```

#### `Str::containsAll()` {.collection-method}

`Str::containsAll` 方法用于判断给定字符串是否包含指定数组中的**所有值**：

```php
use Illuminate\Support\Str;

$containsAll = Str::containsAll('This is my name', ['my', 'name']);

// true
```

你可以通过将 `ignoreCase` 参数设置为 `true` 来禁用大小写敏感：

```php
use Illuminate\Support\Str;

$containsAll = Str::containsAll('This is my name', ['MY', 'NAME'], ignoreCase: true);

// true
```

#### `Str::doesntContain()` {.collection-method}

`Str::doesntContain` 方法用于判断给定字符串**不包含**指定的值。
默认情况下，该方法区分大小写：

```php
use Illuminate\Support\Str;

$doesntContain = Str::doesntContain('This is name', 'my');

// true
```

你也可以传递一个值数组，用来判断给定字符串是否不包含数组中的任意值：

```php
use Illuminate\Support\Str;

$doesntContain = Str::doesntContain('This is name', ['my', 'foo']);

// true
```

你可以通过将 `ignoreCase` 参数设置为 `true` 来禁用大小写敏感：

```php
use Illuminate\Support\Str;

$doesntContain = Str::doesntContain('This is name', 'MY', ignoreCase: true);

// true
```

#### `Str::deduplicate()` {.collection-method}

`Str::deduplicate` 方法会将字符串中某个字符的连续出现替换为该字符的单个实例。
默认情况下，该方法会对空格进行去重：

```php
use Illuminate\Support\Str;

$result = Str::deduplicate('The   Laravel   Framework');

// The Laravel Framework
```



你可以通过在方法中传递第二个参数来指定需要去重的字符：

```php
use Illuminate\Support\Str;

$result = Str::deduplicate('The---Laravel---Framework', '-');

// The-Laravel-Framework
```

#### `Str::endsWith()` {.collection-method}

`Str::endsWith` 方法用于判断给定字符串是否以指定的值结尾：

```php
use Illuminate\Support\Str;

$result = Str::endsWith('This is my name', 'name');

// true
```

你也可以传递一个值数组，用来判断给定字符串是否以数组中的任意一个值结尾：

```php
use Illuminate\Support\Str;

$result = Str::endsWith('This is my name', ['name', 'foo']);

// true

$result = Str::endsWith('This is my name', ['this', 'foo']);

// false
```

#### `Str::excerpt()` {.collection-method}

`Str::excerpt` 方法会从给定字符串中提取包含指定短语的**片段**，并截取该短语第一次出现的位置附近的内容：

```php
use Illuminate\Support\Str;

$excerpt = Str::excerpt('This is my name', 'my', [
    'radius' => 3
]);

// '...is my na...'
```

`radius` 选项（默认值为 `100`）允许你定义在截取字符串时短语前后各显示多少个字符。

此外，你还可以使用 `omission` 选项定义在截取字符串的前后所附加的内容：

```php
use Illuminate\Support\Str;

$excerpt = Str::excerpt('This is my name', 'name', [
    'radius' => 3,
    'omission' => '(...) '
]);

// '(...) my name'
```

#### `Str::finish()` {.collection-method}

`Str::finish` 方法会在字符串末尾追加一个指定值的单个实例（如果该字符串尚未以该值结尾）：

```php
use Illuminate\Support\Str;

$adjusted = Str::finish('this/string', '/');

// this/string/

$adjusted = Str::finish('this/string/', '/');

// this/string/
```



#### `Str::headline()` {.collection-method}

`Str::headline` 方法会将由大小写、连字符或下划线分隔的字符串转换为**空格分隔**的字符串，并将每个单词的首字母大写：

```php
use Illuminate\Support\Str;

$headline = Str::headline('steve_jobs');

// Steve Jobs

$headline = Str::headline('EmailNotificationSent');

// Email Notification Sent
```

#### `Str::inlineMarkdown()` {.collection-method}

`Str::inlineMarkdown` 方法使用 [CommonMark](https://commonmark.thephpleague.com/) 将 GitHub 风格的 Markdown 转换为 **行内 HTML**。
不过，与 `markdown` 方法不同，它不会将所有生成的 HTML 包裹在块级元素中：

```php
use Illuminate\Support\Str;

$html = Str::inlineMarkdown('**Laravel**');

// <strong>Laravel</strong>
```

#### Markdown 安全性

默认情况下，Markdown 支持原始 HTML，这在处理用户输入时可能导致跨站脚本攻击（XSS）漏洞。
根据 [CommonMark 安全文档](https://commonmark.thephpleague.com/security/)，你可以使用 `html_input` 选项来转义或移除原始 HTML，
并通过 `allow_unsafe_links` 选项指定是否允许不安全的链接。
如果你需要允许部分原始 HTML，应当在编译后的 Markdown 上再使用 HTML Purifier 进行过滤：

```php
use Illuminate\Support\Str;

Str::inlineMarkdown('Inject: <script>alert("Hello XSS!");</script>', [
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// Inject: alert(&quot;Hello XSS!&quot;);
```

#### `Str::is()` {.collection-method}

`Str::is` 方法用于判断给定字符串是否与指定模式匹配。
星号 `*` 可以作为通配符使用：

```php
use Illuminate\Support\Str;

$matches = Str::is('foo*', 'foobar');

// true

$matches = Str::is('baz*', 'foobar');

// false
```



你可以通过将 `ignoreCase` 参数设置为 `true` 来禁用大小写敏感：

```php
use Illuminate\Support\Str;

$matches = Str::is('*.jpg', 'photo.JPG', ignoreCase: true);

// true
```

#### `Str::isAscii()` {.collection-method}

`Str::isAscii` 方法用于判断给定字符串是否是 **7 位 ASCII**：

```php
use Illuminate\Support\Str;

$isAscii = Str::isAscii('Taylor');

// true

$isAscii = Str::isAscii('ü');

// false
```

#### `Str::isJson()` {.collection-method}

`Str::isJson` 方法用于判断给定字符串是否是合法的 JSON：

```php
use Illuminate\Support\Str;

$result = Str::isJson('[1,2,3]');

// true

$result = Str::isJson('{"first": "John", "last": "Doe"}');

// true

$result = Str::isJson('{first: "John", last: "Doe"}');

// false
```

#### `Str::isUrl()` {.collection-method}

`Str::isUrl` 方法用于判断给定字符串是否是合法的 URL：

```php
use Illuminate\Support\Str;

$isUrl = Str::isUrl('http://example.com');

// true

$isUrl = Str::isUrl('laravel');

// false
```

`isUrl` 方法默认会将多种协议视为合法。
不过，你可以通过向 `isUrl` 方法传递协议数组来指定哪些协议是合法的：

```php
$isUrl = Str::isUrl('http://example.com', ['http', 'https']);
```

#### `Str::isUlid()` {.collection-method}

`Str::isUlid` 方法用于判断给定字符串是否是合法的 **ULID**：

```php
use Illuminate\Support\Str;

$isUlid = Str::isUlid('01gd6r360bp37zj17nxb55yv40');

// true

$isUlid = Str::isUlid('laravel');

// false
```

#### `Str::isUuid()` {.collection-method}

`Str::isUuid` 方法用于判断给定字符串是否是合法的 **UUID**：

```php
use Illuminate\Support\Str;

$isUuid = Str::isUuid('a0a2a2d2-0b87-4a18-83f2-2529882be2de');

// true

$isUuid = Str::isUuid('laravel');

// false
```



#### `Str::kebab()` {.collection-method}

`Str::kebab` 方法将给定字符串转换为 **kebab-case**（短横线分隔的小写格式）：

```php
use Illuminate\Support\Str;

$converted = Str::kebab('fooBar');

// foo-bar
```

#### `Str::lcfirst()` {.collection-method}

`Str::lcfirst` 方法返回首字母小写的字符串：

```php
use Illuminate\Support\Str;

$string = Str::lcfirst('Foo Bar');

// foo Bar
```

#### `Str::length()` {.collection-method}

`Str::length` 方法返回给定字符串的长度：

```php
use Illuminate\Support\Str;

$length = Str::length('Laravel');

// 7
```

#### `Str::limit()` {.collection-method}

`Str::limit` 方法会将给定字符串截断为指定长度：

```php
use Illuminate\Support\Str;

$truncated = Str::limit('The quick brown fox jumps over the lazy dog', 20);

// The quick brown fox...
```

你可以向方法传递第三个参数，用来修改截断字符串后追加的内容：

```php
$truncated = Str::limit('The quick brown fox jumps over the lazy dog', 20, ' (...)');

// The quick brown fox (...)
```

如果希望在截断时保留完整的单词，可以使用 `preserveWords` 参数。
当该参数为 `true` 时，字符串会在最近的完整单词边界处被截断：

```php
$truncated = Str::limit('The quick brown fox', 12, preserveWords: true);

// The quick...
```

#### `Str::lower()` {.collection-method}

`Str::lower` 方法将给定字符串转换为小写：

```php
use Illuminate\Support\Str;

$converted = Str::lower('LARAVEL');

// laravel
```

#### `Str::markdown()` {.collection-method}

`Str::markdown` 方法使用 [CommonMark](https://commonmark.thephpleague.com/) 将 GitHub 风格的 Markdown 转换为 HTML：

```php
use Illuminate\Support\Str;

$html = Str::markdown('# Laravel');

// <h1>Laravel</h1>

$html = Str::markdown('# Taylor <b>Otwell</b>', [
    'html_input' => 'strip',
]);

// <h1>Taylor Otwell</h1>
```



#### Markdown 安全性

默认情况下，Markdown 支持原始 HTML，当与原始用户输入一起使用时，会暴露跨站脚本（XSS）漏洞。根据 [CommonMark 安全性文档](https://commonmark.thephpleague.com/security/)，你可以使用 `html_input` 选项来转义或去除原始 HTML，并使用 `allow_unsafe_links` 选项来指定是否允许不安全的链接。如果你需要允许一些原始 HTML，你应该将已编译的 Markdown 通过一个 HTML Purifier：

```php
use Illuminate\Support\Str;

Str::markdown('Inject: <script>alert("Hello XSS!");</script>', [
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// <p>Inject: alert(&quot;Hello XSS!&quot;);</p>
```

#### `Str::mask()` {.collection-method}

`Str::mask` 方法用一个重复的字符掩盖字符串的一部分，可以用来模糊处理字符串的片段，比如电子邮件地址和电话号码：

```php
use Illuminate\Support\Str;

$string = Str::mask('taylor@example.com', '*', 3);

// tay***************
```

如果需要，你可以将一个负数作为第三个参数传给 `mask` 方法，这会指示该方法从字符串末尾给定的距离处开始掩盖：

```php
$string = Str::mask('taylor@example.com', '*', -15, 3);

// tay***@example.com
```

#### `Str::orderedUuid()` {.collection-method}

`Str::orderedUuid` 方法生成一个“时间戳优先”的 UUID，它可以高效地存储在一个有索引的数据库列中。使用此方法生成的每个 UUID 将会排在之前使用该方法生成的 UUID 之后：

```php
use Illuminate\Support\Str;

return (string) Str::orderedUuid();
```



#### `Str::padBoth()` {.collection-method}

`Str::padBoth` 方法封装了 PHP 的 `str_pad` 函数，在字符串的两边用另一个字符串填充，直到最终字符串达到所需的长度：

```php
use Illuminate\Support\Str;

$padded = Str::padBoth('James', 10, '_');

// '__James___'

$padded = Str::padBoth('James', 10);

// '  James   '
```

#### `Str::padLeft()` {.collection-method}

`Str::padLeft` 方法封装了 PHP 的 `str_pad` 函数，在字符串的左边用另一个字符串填充，直到最终字符串达到所需的长度：

```php
use Illuminate\Support\Str;

$padded = Str::padLeft('James', 10, '-=');

// '-=-=-James'

$padded = Str::padLeft('James', 10);

// '     James'
```

#### `Str::padRight()` {.collection-method}

`Str::padRight` 方法封装了 PHP 的 `str_pad` 函数，在字符串的右边用另一个字符串填充，直到最终字符串达到所需的长度：

```php
use Illuminate\Support\Str;

$padded = Str::padRight('James', 10, '-');

// 'James-----'

$padded = Str::padRight('James', 10);

// 'James     '
```

#### `Str::password()` {.collection-method}

`Str::password` 方法可用于生成一个给定长度的安全随机密码。密码将由字母、数字、符号和空格的组合构成。默认情况下，密码长度为 32 个字符：

```php
use Illuminate\Support\Str;

$password = Str::password();

// 'EbJo2vE-AS:U,$%_gkrV4n,q~1xy/-_4'

$password = Str::password(12);

// 'qwuar>#V|i]N'
```

#### `Str::plural()` {.collection-method}

`Str::plural` 方法将一个单数单词字符串转换为它的复数形式。此函数支持 [Laravel 复数化工具所支持的任何语言](/docs/laravel/12.x/localization#pluralization-language)：

```php
use Illuminate\Support\Str;

$plural = Str::plural('car');

// cars

$plural = Str::plural('child');

// children
```



你可以提供一个整数作为函数的第二个参数，以获取字符串的单数形式或复数形式：

```php
use Illuminate\Support\Str;

$plural = Str::plural('child', 2);

// children

$singular = Str::plural('child', 1);

// child
```

#### `Str::pluralStudly()` {.collection-method}

`Str::pluralStudly` 方法将一个以驼峰格式（Studly Caps Case）编写的单数单词字符串转换为其复数形式。此函数支持 [Laravel 复数化工具所支持的任何语言](/docs/laravel/12.x/localization#pluralization-language)：

```php
use Illuminate\Support\Str;

$plural = Str::pluralStudly('VerifiedHuman');

// VerifiedHumans

$plural = Str::pluralStudly('UserFeedback');

// UserFeedback
```

你可以提供一个整数作为函数的第二个参数，以获取字符串的单数形式或复数形式：

```php
use Illuminate\Support\Str;

$plural = Str::pluralStudly('VerifiedHuman', 2);

// VerifiedHumans

$singular = Str::pluralStudly('VerifiedHuman', 1);

// VerifiedHuman
```

#### `Str::position()` {.collection-method}

`Str::position` 方法返回子字符串在字符串中第一次出现的位置。 如果子字符串在给定字符串中不存在，则返回 `false`：

```php
use Illuminate\Support\Str;

$position = Str::position('Hello, World!', 'Hello');

// 0

$position = Str::position('Hello, World!', 'W');

// 7
```

#### `Str::random()` {.collection-method}

`Str::random` 方法生成指定长度的随机字符串。此函数使用 PHP 的 `random_bytes` 函数：

```php
use Illuminate\Support\Str;

$random = Str::random(40);
```

在测试过程中，伪造 `Str::random` 方法返回的值可能会很有用。为此，你可以使用 `createRandomStringsUsing` 方法：

```php
Str::createRandomStringsUsing(function () {
    return 'fake-random-string';
});
```



你可以通过调用 `createRandomStringsNormally` 方法来让 `random` 方法恢复正常生成随机字符串：

```php
Str::createRandomStringsNormally();
```

#### `Str::remove()` {.collection-method}

`Str::remove` 方法从字符串中移除指定的值或值数组：

```php
use Illuminate\Support\Str;

$string = 'Peter Piper picked a peck of pickled peppers.';

$removed = Str::remove('e', $string);

// Ptr Pipr pickd a pck of pickld ppprs.
```

你也可以向 `remove` 方法传递第三个参数 `false`，在移除字符串时忽略大小写。

#### `Str::repeat()` {.collection-method}

`Str::repeat` 方法重复给定的字符串：

```php
use Illuminate\Support\Str;

$string = 'a';

$repeat = Str::repeat($string, 5);

// aaaaa
```

#### `Str::replace()` {.collection-method}

`Str::replace` 方法替换字符串中的指定内容：

```php
use Illuminate\Support\Str;

$string = 'Laravel 11.x';

$replaced = Str::replace('11.x', '12.x', $string);

// Laravel 12.x
```

`replace` 方法也接受一个 `caseSensitive` 参数。默认情况下，`replace` 方法区分大小写：

```php
Str::replace('Framework', 'Laravel', caseSensitive: false);
```

#### `Str::replaceArray()` {.collection-method}

`Str::replaceArray` 方法使用数组顺序依次替换字符串中的指定值：

```php
use Illuminate\Support\Str;

$string = 'The event will take place between ? and ?';

$replaced = Str::replaceArray('?', ['8:30', '9:00'], $string);

// The event will take place between 8:30 and 9:00
```

#### `Str::replaceFirst()` {.collection-method}

`Str::replaceFirst` 方法替换字符串中**第一次出现**的指定值：

```php
use Illuminate\Support\Str;

$replaced = Str::replaceFirst('the', 'a', 'the quick brown fox jumps over the lazy dog');

// a quick brown fox jumps over the lazy dog
```



#### `Str::replaceLast()` {.collection-method}

`Str::replaceLast` 方法替换字符串中**最后一次出现**的指定值：


```php
use Illuminate\Support\Str;

$replaced = Str::replaceLast('the', 'a', 'the quick brown fox jumps over the lazy dog');

// the quick brown fox jumps over a lazy dog
```

#### `Str::replaceMatches()` {.collection-method}

`Str::replaceMatches` 方法将匹配给定模式的字符串部分替换为指定的替换字符串：

```php
use Illuminate\Support\Str;

$replaced = Str::replaceMatches(
    pattern: '/[^A-Za-z0-9]++/',
    replace: '',
    subject: '(+1) 501-555-1000'
)

// '15015551000'
```

`replaceMatches` 方法也可以接受一个闭包函数，闭包会对每个匹配的字符串部分调用，你可以在闭包中执行替换逻辑并返回替换后的值：

```php
use Illuminate\Support\Str;

$replaced = Str::replaceMatches('/\d/', function (array $matches) {
    return '['.$matches[0].']';
}, '123');

// '[1][2][3]'
```

#### `Str::replaceStart()` {.collection-method}

`Str::replaceStart` 方法仅在给定值出现在字符串开头时替换第一次出现的值：

```php
use Illuminate\Support\Str;

$replaced = Str::replaceStart('Hello', 'Laravel', 'Hello World');

// Laravel World

$replaced = Str::replaceStart('World', 'Laravel', 'Hello World');

// Hello World
```

#### `Str::replaceEnd()` {.collection-method}

`Str::replaceEnd` 方法仅在给定值出现在字符串结尾时替换最后一次出现的值：

```php
use Illuminate\Support\Str;

$replaced = Str::replaceEnd('World', 'Laravel', 'Hello World');

// Hello Laravel

$replaced = Str::replaceEnd('Hello', 'Laravel', 'Hello World');

// Hello World
```



<a name="method-str-reverse"></a>
#### `Str::reverse()`
`Str::reverse` 方法反转给定的字符串：

```php
use Illuminate\Support\Str;

$reversed = Str::reverse('Hello World');

// dlroW olleH
```

<a name="method-str-singular"></a>
#### `Str::singular()`

`Str::singular` 方法将字符串转换为单数形式. 此函数支持 [laravel复数转换器支持的任何语言](/docs/laravel/12.x/localization#pluralization-language):

```php
use Illuminate\Support\Str;

$singular = Str::singular('cars');

// car

$singular = Str::singular('children');

// child
```

<a name="method-str-slug"></a>
#### `Str::slug()`

`Str::slug` 方法根据给定的字符串生成 URL 友好的「slug」：

```php
use Illuminate\Support\Str;

$slug = Str::slug('Laravel 5 Framework', '-');

// laravel-5-framework
```

<a name="method-snake-case"></a>
#### `Str::snake()`

`Str::snake` 方法将给定的字符串转换为蛇形命名格式 `snake_case` ：

```php
use Illuminate\Support\Str;

$converted = Str::snake('fooBar');

// foo_bar

$converted = Str::snake('fooBar', '-');

// foo-bar
```

<a name="method-str-squish"></a>
#### `Str::squish()`

`Str::squish` 方法从字符串中删除所有多余的空格，包括单词之间的多余的空格：

```php
use Illuminate\Support\Str;

$string = Str::squish('    laravel    framework    ');

// laravel framework
```

<a name="method-str-start"></a>
#### `Str::start()`

`Str::start` 如果字符串尚未以该值开头，则`Str::start`方法将给定值的单个实例添加到字符串中：

```php
use Illuminate\Support\Str;

$adjusted = Str::start('this/string', '/');

// /this/string

$adjusted = Str::start('/this/string', '/');

// /this/string
```

<a name="method-starts-with"></a>
#### `Str::startsWith()`

`Str::startsWith` 方法检测给定的字符串是否以给定的值开头：

```php
use Illuminate\Support\Str;

$result = Str::startsWith('This is my name', 'This');

// true
```



如果传递了一个可能值数组，则当字符串以数组中任意给定值开头时 `startsWith` 方法将返回 `true`：

```php
$result = Str::startsWith('This is my name', ['This', 'That', 'There']);

// true
```

<a name="method-studly-case"></a>
#### `Str::studly()` {.collection-method}

`Str::studly` 方法将给定的字符串转换为 `StudlyCase` ：

```php
use Illuminate\Support\Str;

$converted = Str::studly('foo_bar');

// FooBar
```

<a name="method-str-substr"></a>
#### `Str::substr()` {.collection-method}

`Str::substr` 方法返回由开始位置和长度参数指定的字符串部分：

```php
use Illuminate\Support\Str;

$converted = Str::substr('The Laravel Framework', 4, 7);

// Laravel
```

<a name="method-str-substrcount"></a>
#### `Str::substrCount()` {.collection-method}

`Str::substrCount` 方法返回给定字符串中给定值出现的次数：

```php
use Illuminate\Support\Str;

$count = Str::substrCount('If you like ice cream, you will like snow cones.', 'like');

// 2
```

<a name="method-str-substrreplace"></a>
#### `Str::substrReplace()` {.collection-method}

`Str::substrReplace` 方法替换字符串中某一部分内的文本，从第三个参数指定的位置开始，替换第四个参数指定的字符数。传递 `0` 给该方法的第四个参数将在指定位置插入字符串，但不替换字符串中的任何现有字符：

```php
use Illuminate\Support\Str;

$result = Str::substrReplace('1300', ':', 2);
// 13:

$result = Str::substrReplace('1300', ':', 2, 0);
// 13:00
```

<a name="method-str-swap"></a>
#### `Str::swap()` {.collection-method}

`Str::swap` 方法使用 PHP 的函数 `strtr` 替换给定字符串中的多个值：

```php
use Illuminate\Support\Str;

$string = Str::swap([
    'Tacos' => 'Burritos',
    'great' => 'fantastic',
], 'Tacos are great!');

// Burritos are fantastic!
```



<a name="method-take"></a>
#### `Str::take()` {.collection-method}

`Str::take` 方法返回字符串开头指定数量的字符：

```php
use Illuminate\Support\Str;

$taken = Str::take('Build something amazing!', 5);

// Build
```

<a name="method-title-case"></a>
#### `Str::title()` {.collection-method}

`Str::title` 方法将给定的字符串转换为 `Title Case`:

```php
use Illuminate\Support\Str;

$converted = Str::title('a nice title uses the correct case');

// A Nice Title Uses The Correct Case
```

<a name="method-str-to-base64"></a>
#### `Str::toBase64()` {.collection-method}

`Str::toBase64` 方法将给定的字符串转换为 Base64 编码：

```php
use Illuminate\Support\Str;

$base64 = Str::toBase64('Laravel');

// TGFyYXZlbA==
```

<a name="method-str-transliterate"></a>
#### `Str::transliterate()` {.collection-method}

`Str::transliterate` 方法会尝试将给定字符串转换为其最接近的 ASCII 字符形式。

```php
use Illuminate\Support\Str;

$email = Str::transliterate('ⓣⓔⓢⓣ@ⓛⓐⓡⓐⓥⓔⓛ.ⓒⓞⓜ');

// 'test@laravel.com'
```

<a name="method-str-trim"></a>
#### `Str::trim()` {.collection-method}

`Str::trim` 方法从给定字符串的开头和结尾删除空格（或其他字符）。与 PHP 的原生的 `trim` 函数不同，`Str::trim` 方法还会删除 unicode 空格字符：

```php
use Illuminate\Support\Str;

$string = Str::trim(' foo bar ');

// 'foo bar'
```

<a name="method-str-ltrim"></a>
#### `Str::ltrim()` {.collection-method}

`Str::ltrim` 方法从给定字符串的开头删除空格（或其他字符）。与 PHP 的原生的 `ltrim` 函数不同,`Str::ltrim` 方法还会删除 unicode 空格字符：

```php
use Illuminate\Support\Str;

$string = Str::ltrim('  foo bar  ');

// 'foo bar  '
```

<a name="method-str-rtrim"></a>
#### `Str::rtrim()` {.collection-method}



`Str::rtrim` 方法从给定字符串的末尾删除空格（或其他字符）。与 PHP 原生的 `rtrim` 函数不同，`Str::rtrim` 方法还会删除 unicode 空格字符：

```php
use Illuminate\Support\Str;

$string = Str::rtrim('  foo bar  ');

// '  foo bar'
```

<a name="method-str-ucfirst"></a>
#### `Str::ucfirst()` {.collection-method}

`Str::ucfirst` 方法返回首字母大写的给定字符串：
```php
use Illuminate\Support\Str;

$string = Str::ucfirst('foo bar');

// Foo bar
```

<a name="method-str-ucsplit"></a>
#### `Str::ucsplit()` {.collection-method}

`Str::ucsplit` 方法将给定的字符串按大写字符拆分为数组：
```php
use Illuminate\Support\Str;

$segments = Str::ucsplit('FooBar');

// [0 => 'Foo', 1 => 'Bar']
```

<a name="method-str-upper"></a>
#### `Str::upper()` {.collection-method}

`Str::upper` 方法将给定的字符串转换为大写：
```php
use Illuminate\Support\Str;

$string = Str::upper('laravel');

// LARAVEL
```

<a name="method-str-ulid"></a>
#### `Str::ulid()` {.collection-method}

`Str::ulid` 方法生成一个 ULID，它是一个紧凑的、按时间排序的唯一标识符：
```php
use Illuminate\Support\Str;

return (string) Str::ulid();

// 01gd6r360bp37zj17nxb55yv40
```



如果您想要获取 `Illuminate\Support\Carbon` 表示创建给定 ULID 的日期和时间的日期实例，您可以使用 Laravel Carbon 集成提供 `createFromId` 的方法：

```php
use Illuminate\Support\Carbon;
use Illuminate\Support\Str;

$date = Carbon::createFromId((string) Str::ulid());
```
在测试期间，「伪造」方法 `Str::ulid` 返回的值可能会很有用。为此，您可以使用 `createUlidsUsing` 方法：

```php
use Symfony\Component\Uid\Ulid;

Str::createUlidsUsing(function () {
    return new Ulid('01HRDBNHHCKNW2AK4Z29SN82T9');
});
```



要指示 `ulid` 方法恢复正常生成 ULID，你可以调用 `createUlidsNormally` 方法：

```php
Str::createUlidsNormally();
```

#### `Str::unwrap()` {.collection-method}

`Str::unwrap` 方法会移除给定字符串开头和结尾的指定内容：

```php
use Illuminate\Support\Str;

Str::unwrap('-Laravel-', '-');

// Laravel

Str::unwrap('{framework: "Laravel"}', '{', '}');

// framework: "Laravel"
```

#### `Str::uuid()` {.collection-method}

`Str::uuid` 方法生成一个 UUID（版本 4）：

```php
use Illuminate\Support\Str;

return (string) Str::uuid();
```

在测试过程中，可能需要“伪造”`Str::uuid` 方法返回的值。为此，你可以使用 `createUuidsUsing` 方法：

```php
use Ramsey\Uuid\Uuid;

Str::createUuidsUsing(function () {
    return Uuid::fromString('eadbfeac-5258-45c2-bab7-ccb9b5ef74f9');
});
```

要指示 `uuid` 方法恢复正常生成 UUID，你可以调用 `createUuidsNormally` 方法：

```php
Str::createUuidsNormally();
```

#### `Str::uuid7()` {.collection-method}

`Str::uuid7` 方法生成一个 UUID（版本 7）：

```php
use Illuminate\Support\Str;

return (string) Str::uuid7();
```

可以传入一个可选参数 `DateTimeInterface`，用于生成有序的 UUID：

```php
return (string) Str::uuid7(time: now());
```

#### `Str::wordCount()` {.collection-method}

`Str::wordCount` 方法返回字符串中包含的单词数：

```php
use Illuminate\Support\Str;

Str::wordCount('Hello, world!'); // 2
```

#### `Str::wordWrap()` {.collection-method}

`Str::wordWrap` 方法将字符串按指定字符数进行换行：

```php
use Illuminate\Support\Str;

$text = "The quick brown fox jumped over the lazy dog."

Str::wordWrap($text, characters: 20, break: "<br />\n");

/*
The quick brown fox<br />
jumped over the lazy<br />
dog.
*/
```



<a name="method-str-words"></a>
#### `Str::words()` {.collection-method}

`Str::words` 方法可以限制一个字符串中的单词数量。 向该方法的第三个参数传入一个附加字符串，可以指定添加到被截断字符串末尾的字符串：

```php
use Illuminate\Support\Str;

return Str::words('Perfectly balanced, as all things should be.', 3, ' >>>');

// Perfectly balanced, as >>>
```

<a name="method-str-wrap"></a>
#### `Str::wrap()` {.collection-method}

`Str::wrap` 方法可以给指定的字符串添加额外的字符串或字符串对：

```php
use Illuminate\Support\Str;

Str::wrap('Laravel', '"');

// "Laravel"

Str::wrap('is', before: 'This ', after: ' Laravel!');

// This is Laravel!
```

<a name="method-str"></a>
#### `str()` {.collection-method}

`str` 方法返回一个指定字符串新的 `Illuminate\Support\Stringable` 实例。这个方法等价 `Str::of` 方法：

```php
$string = str('Taylor')->append(' Otwell');

// 'Taylor Otwell'
```

如果没有向 `str` 方法添加参数，它会返回一个 `Illuminate\Support\Str` 实例：

```php
$snake = str()->snake('FooBar');

// 'foo_bar'
```

<a name="method-trans"></a>
#### `trans()` {.collection-method}

`trans` 方法通过 [language files](/docs/laravel/12.x/localization) 翻译指定的关键字：

```php
echo trans('messages.welcome');
```

如果指定的关键字不存在， `trans` 方法将返回关键字本身。所以，如果翻译的关键字不存在，上面的示例中 `trans` 方法将返回 `messages.welcome` 。

<a name="method-trans-choice"></a>
#### `trans_choice()` {.collection-method}

`trans_choice` 方法通过动态值翻译指定的关键字：

```php
echo trans_choice('messages.notifications', $unreadCount);
```



如果指定的翻译键不存在，`trans_choice` 函数将返回给定的键。因此，使用上面的示例，如果翻译键不存在，`trans_choice` 函数将返回 `messages.notifications`。

## 流式字符串（Fluent Strings）

流式字符串提供了一种更流畅、面向对象的接口来处理字符串值，允许你将多个字符串操作链式调用，使语法比传统字符串操作更易读。

#### `after` {.collection-method}

`after` 方法返回字符串中指定值之后的所有内容。如果字符串中不存在该值，将返回整个字符串：

```php
use Illuminate\Support\Str;

$slice = Str::of('This is my name')->after('This is');

// ' my name'
```

#### `afterLast` {.collection-method}

`afterLast` 方法返回字符串中指定值最后一次出现之后的所有内容。如果字符串中不存在该值，将返回整个字符串：

```php
use Illuminate\Support\Str;

$slice = Str::of('App\Http\Controllers\Controller')->afterLast('\\');

// 'Controller'
```

#### `apa` {.collection-method}

`apa` 方法将给定字符串转换为标题大小写（Title Case），遵循 [APA 指南](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case)：

```php
use Illuminate\Support\Str;

$converted = Str::of('a nice title uses the correct case')->apa();

// A Nice Title Uses the Correct Case
```

#### `append` {.collection-method}

`append` 方法将给定的值追加到字符串后：

```php
use Illuminate\Support\Str;

$string = Str::of('Taylor')->append(' Otwell');

// 'Taylor Otwell'
```



#### `ascii` {.collection-method}

`ascii` 方法会尝试将字符串音译（transliterate）为 ASCII 值：

```php
use Illuminate\Support\Str;

$string = Str::of('ü')->ascii();

// 'u'
```

#### `basename` {.collection-method}

`basename` 方法返回给定字符串的最后名称部分：

```php
use Illuminate\Support\Str;

$string = Str::of('/foo/bar/baz')->basename();

// 'baz'
```

如果需要，你可以提供一个“扩展名”，它将从最后的名称部分中移除：

```php
use Illuminate\Support\Str;

$string = Str::of('/foo/bar/baz.jpg')->basename('.jpg');

// 'baz'
```

#### `before` {.collection-method}

`before` 方法返回字符串中指定值之前的所有内容：

```php
use Illuminate\Support\Str;

$slice = Str::of('This is my name')->before('my name');

// 'This is '
```

#### `beforeLast` {.collection-method}

`beforeLast` 方法返回字符串中指定值最后一次出现之前的所有内容：

```php
use Illuminate\Support\Str;

$slice = Str::of('This is my name')->beforeLast('is');

// 'This '
```

#### `between` {.collection-method}

`between` 方法返回字符串中两个值之间的部分内容：

```php
use Illuminate\Support\Str;

$converted = Str::of('This is my name')->between('This', 'name');

// ' is my '
```

#### `betweenFirst` {.collection-method}

`betweenFirst` 方法返回字符串中两个值之间的最小可能部分：

```php
use Illuminate\Support\Str;

$converted = Str::of('[a] bc [d]')->betweenFirst('[', ']');

// 'a'
```



#### `camel` {.collection-method}

`camel` 方法将给定字符串转换为 `camelCase`：

```php
use Illuminate\Support\Str;

$converted = Str::of('foo_bar')->camel();

// 'fooBar'
```

#### `charAt` {.collection-method}

`charAt` 方法返回指定索引位置的字符。如果索引超出范围，则返回 `false`：

```php
use Illuminate\Support\Str;

$character = Str::of('This is my name.')->charAt(6);

// 's'
```

#### `classBasename` {.collection-method}

`classBasename` 方法返回给定类的类名，并移除类的命名空间：

```php
use Illuminate\Support\Str;

$class = Str::of('Foo\Bar\Baz')->classBasename();

// 'Baz'
```

#### `chopStart` {.collection-method}

`chopStart` 方法仅在给定值出现在字符串开头时，移除该值的第一次出现：

```php
use Illuminate\Support\Str;

$url = Str::of('https://laravel.com')->chopStart('https://');

// 'laravel.com'
```

你也可以传入一个数组。如果字符串以数组中的任意值开头，则会移除该值：

```php
use Illuminate\Support\Str;

$url = Str::of('http://laravel.com')->chopStart(['https://', 'http://']);

// 'laravel.com'
```

#### `chopEnd` {.collection-method}

`chopEnd` 方法仅在给定值出现在字符串结尾时，移除该值的最后一次出现：

```php
use Illuminate\Support\Str;

$url = Str::of('https://laravel.com')->chopEnd('.com');

// 'https://laravel'
```

你也可以传入一个数组。如果字符串以数组中的任意值结尾，则会移除该值：

```php
use Illuminate\Support\Str;

$url = Str::of('http://laravel.com')->chopEnd(['.com', '.io']);

// 'http://laravel'
```



#### `contains` {.collection-method}

`contains` 方法用于判断给定字符串是否包含指定的值。默认情况下，该方法区分大小写：

```php
use Illuminate\Support\Str;

$contains = Str::of('This is my name')->contains('my');

// true
```

你也可以传入一个值的数组，用于判断给定字符串是否包含数组中的任意值：

```php
use Illuminate\Support\Str;

$contains = Str::of('This is my name')->contains(['my', 'foo']);

// true
```

通过将 `ignoreCase` 参数设置为 `true`，可以禁用大小写敏感：

```php
use Illuminate\Support\Str;

$contains = Str::of('This is my name')->contains('MY', ignoreCase: true);

// true
```

#### `containsAll` {.collection-method}

`containsAll` 方法用于判断给定字符串是否包含数组中的所有值：

```php
use Illuminate\Support\Str;

$containsAll = Str::of('This is my name')->containsAll(['my', 'name']);

// true
```

通过将 `ignoreCase` 参数设置为 `true`，可以禁用大小写敏感：

```php
use Illuminate\Support\Str;

$containsAll = Str::of('This is my name')->containsAll(['MY', 'NAME'], ignoreCase: true);

// true
```

#### `deduplicate` {.collection-method}

`deduplicate` 方法会将字符串中连续重复的字符替换为单个字符。默认情况下，该方法会去除连续的空格：

```php
use Illuminate\Support\Str;

$result = Str::of('The   Laravel   Framework')->deduplicate();

// The Laravel Framework
```

你也可以指定其他要去重的字符，通过将其作为方法的第二个参数传入：

```php
use Illuminate\Support\Str;

$result = Str::of('The---Laravel---Framework')->deduplicate('-');

// The-Laravel-Framework
```



#### `dirname` {.collection-method}

`dirname` 方法返回给定字符串的父目录部分：

```php
use Illuminate\Support\Str;

$string = Str::of('/foo/bar/baz')->dirname();

// '/foo/bar'
```

如有需要，你可以指定希望从字符串中裁剪掉多少级目录：

```php
use Illuminate\Support\Str;

$string = Str::of('/foo/bar/baz')->dirname(2);

// '/foo'
```

#### `endsWith` {.collection-method}

`endsWith` 方法用于判断给定字符串是否以指定的值结尾：

```php
use Illuminate\Support\Str;

$result = Str::of('This is my name')->endsWith('name');

// true
```

你也可以传入一个数组，用于判断给定字符串是否以数组中的任意一个值结尾：

```php
use Illuminate\Support\Str;

$result = Str::of('This is my name')->endsWith(['name', 'foo']);

// true

$result = Str::of('This is my name')->endsWith(['this', 'foo']);

// false
```

#### `exactly` {.collection-method}

`exactly` 方法用于判断给定字符串是否与另一个字符串完全相同：

```php
use Illuminate\Support\Str;

$result = Str::of('Laravel')->exactly('Laravel');

// true
```

#### `excerpt` {.collection-method}

`excerpt` 方法从字符串中提取一个摘要，该摘要匹配字符串中第一次出现的指定短语：

```php
use Illuminate\Support\Str;

$excerpt = Str::of('This is my name')->excerpt('my', [
    'radius' => 3
]);

// '...is my na...'
```

`radius` 选项的默认值为 `100`，用于定义在被截断字符串两侧应显示的字符数量。



此外，你可以使用 `omission` 选项来修改在被截断字符串前后添加的字符串：

```php
use Illuminate\Support\Str;

$excerpt = Str::of('This is my name')->excerpt('name', [
    'radius' => 3,
    'omission' => '(...) '
]);

// '(...) my name'
```

#### `explode` {.collection-method}

`explode` 方法使用给定的分隔符拆分字符串，并返回一个包含拆分后各个片段的集合：

```php
use Illuminate\Support\Str;

$collection = Str::of('foo bar baz')->explode(' ');

// collect(['foo', 'bar', 'baz'])
```

#### `finish` {.collection-method}

`finish` 方法会在字符串末尾添加一个给定值的单个实例（如果字符串尚未以该值结尾）：

```php
use Illuminate\Support\Str;

$adjusted = Str::of('this/string')->finish('/');

// this/string/

$adjusted = Str::of('this/string/')->finish('/');

// this/string/
```

#### `headline` {.collection-method}

`headline` 方法会将使用大小写、连字符或下划线分隔的字符串转换为以空格分隔的字符串，并将每个单词的首字母大写：

```php
use Illuminate\Support\Str;

$headline = Str::of('taylor_otwell')->headline();

// Taylor Otwell

$headline = Str::of('EmailNotificationSent')->headline();

// Email Notification Sent
```

#### `inlineMarkdown` {.collection-method}

`inlineMarkdown` 方法使用 [CommonMark](https://commonmark.thephpleague.com/) 将 GitHub 风格的 Markdown 转换为内联 HTML。不过，与 `markdown` 方法不同的是，它不会将生成的所有 HTML 包裹在块级元素中：

```php
use Illuminate\Support\Str;

$html = Str::of('**Laravel**')->inlineMarkdown();

// <strong>Laravel</strong>
```



#### Markdown 安全性

默认情况下，Markdown 支持原始 HTML，这在与原始用户输入一起使用时会暴露跨站脚本（XSS）漏洞。根据 [CommonMark 安全文档](https://commonmark.thephpleague.com/security/) 的说明，你可以使用 `html_input` 选项来转义或移除原始 HTML，并使用 `allow_unsafe_links` 选项来指定是否允许不安全的链接。如果你需要允许部分原始 HTML，应当将已编译的 Markdown 通过 HTML Purifier 进行处理：

```php
use Illuminate\Support\Str;

Str::of('Inject: <script>alert("Hello XSS!");</script>')->inlineMarkdown([
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// Inject: alert(&quot;Hello XSS!&quot;);
```

#### `is` {.collection-method}

`is` 方法用于判断给定字符串是否匹配指定的模式。星号（`*`）可用作通配符：

```php
use Illuminate\Support\Str;

$matches = Str::of('foobar')->is('foo*');

// true

$matches = Str::of('foobar')->is('baz*');

// false
```

#### `isAscii` {.collection-method}

`isAscii` 方法用于判断给定字符串是否为 ASCII 字符串：

```php
use Illuminate\Support\Str;

$result = Str::of('Taylor')->isAscii();

// true

$result = Str::of('ü')->isAscii();

// false
```

#### `isEmpty` {.collection-method}

`isEmpty` 方法用于判断给定字符串是否为空：

```php
use Illuminate\Support\Str;

$result = Str::of('  ')->trim()->isEmpty();

// true

$result = Str::of('Laravel')->trim()->isEmpty();

// false
```

#### `isNotEmpty` {.collection-method}

`isNotEmpty` 方法用于判断给定字符串是否不为空：

```php
use Illuminate\Support\Str;

$result = Str::of('  ')->trim()->isNotEmpty();

// false

$result = Str::of('Laravel')->trim()->isNotEmpty();

// true
```



#### `isJson` {.collection-method}

`isJson` 方法用于判断给定字符串是否为有效的 JSON：

```php
use Illuminate\Support\Str;

$result = Str::of('[1,2,3]')->isJson();

// true

$result = Str::of('{"first": "John", "last": "Doe"}')->isJson();

// true

$result = Str::of('{first: "John", last: "Doe"}')->isJson();

// false
```

#### `isUlid` {.collection-method}

`isUlid` 方法用于判断给定字符串是否为 ULID：

```php
use Illuminate\Support\Str;

$result = Str::of('01gd6r360bp37zj17nxb55yv40')->isUlid();

// true

$result = Str::of('Taylor')->isUlid();

// false
```

#### `isUrl` {.collection-method}

`isUrl` 方法用于判断给定字符串是否为 URL：

```php
use Illuminate\Support\Str;

$result = Str::of('http://example.com')->isUrl();

// true

$result = Str::of('Taylor')->isUrl();

// false
```

`isUrl` 方法会将多种协议视为有效。不过，你可以通过向 `isUrl` 方法传入协议列表，来指定哪些协议应被视为有效：

```php
$result = Str::of('http://example.com')->isUrl(['http', 'https']);
```

#### `isUuid` {.collection-method}

`isUuid` 方法用于判断给定字符串是否为 UUID：

```php
use Illuminate\Support\Str;

$result = Str::of('5ace9ab9-e9cf-4ec6-a19d-5881212a452c')->isUuid();

// true

$result = Str::of('Taylor')->isUuid();

// false
```

#### `kebab` {.collection-method}

`kebab` 方法会将给定字符串转换为 `kebab-case` 格式：

```php
use Illuminate\Support\Str;

$converted = Str::of('fooBar')->kebab();

// foo-bar
```



#### `lcfirst` {.collection-method}

`lcfirst` 方法返回将给定字符串的第一个字符转换为小写后的字符串:

```php
use Illuminate\Support\Str;

$string = Str::of('Foo Bar')->lcfirst();

// foo Bar
```

<a name="method-fluent-str-length"></a>
#### `length` {.collection-method}

`length` 方法返回给定字符串的长度。:

```php
use Illuminate\Support\Str;

$length = Str::of('Laravel')->length();

// 7
```

<a name="method-fluent-str-limit"></a>
#### `limit` {.collection-method}

`limit` 方法将给定的字符串截断到指定的长度。:

```php
use Illuminate\Support\Str;

$truncated = Str::of('The quick brown fox jumps over the lazy dog')->limit(20);

// The quick brown fox...
```

您还可以传递第二个参数来更改将附加到截断字符串末尾的字符串:

```php
$truncated = Str::of('The quick brown fox jumps over the lazy dog')->limit(20, ' (...)');

// The quick brown fox (...)
```

如果您希望在截断字符串时保留完整的单词，可以使用 `preserveWords` 参数。当此参数设置为 `true` 时，, 字符串将被截断到最接近的完整单词边界处:

```php
$truncated = Str::of('The quick brown foxThe quick brown fox')->limit(12, preserveWords: true);

// The quick...
```

<a name="method-fluent-str-lower"></a>
#### `lower` {.collection-method}

`lower` 方法将给定的字符串转换为小写。:

```php
use Illuminate\Support\Str;

$result = Str::of('LARAVEL')->lower();

// 'laravel'
```

<a name="method-fluent-str-markdown"></a>
#### `markdown` {.collection-method}

 `markdown` 该方法将 GitHub 风格的 Markdown 转换为 HTML。:

```php
use Illuminate\Support\Str;

$html = Str::of('# Laravel')->markdown();

// <h1>Laravel</h1>

$html = Str::of('# Taylor <b>Otwell</b>')->markdown([
    'html_input' => 'strip',
]);

// <h1>Taylor Otwell</h1>
```



#### Markdown 安全性

默认情况下，Markdown 支持原始 HTML，这在与原始用户输入一起使用时会暴露跨站脚本（XSS）漏洞。根据 [CommonMark 安全文档](https://commonmark.thephpleague.com/security/) 的说明，你可以使用 `html_input` 选项来转义或移除原始 HTML，并使用 `allow_unsafe_links` 选项来指定是否允许不安全的链接。如果你需要允许部分原始 HTML，应当将已编译的 Markdown 通过 HTML Purifier 进行处理：

```php
use Illuminate\Support\Str;

Str::of('Inject: <script>alert("Hello XSS!");</script>')->markdown([
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// <p>Inject: alert(&quot;Hello XSS!&quot;);</p>
```

#### `mask` {.collection-method}

`mask` 方法会使用重复字符来遮蔽字符串的一部分，可用于混淆诸如电子邮件地址和电话号码等字符串片段：

```php
use Illuminate\Support\Str;

$string = Str::of('taylor@example.com')->mask('*', 3);

// tay***************
```

如有需要，你可以向 `mask` 方法的第三个或第四个参数传入负数，这将指示该方法从字符串末尾起按指定距离开始进行遮蔽：

```php
$string = Str::of('taylor@example.com')->mask('*', -15, 3);

// tay***@example.com

$string = Str::of('taylor@example.com')->mask('*', 4, -4);

// tayl**********.com
```

#### `match` {.collection-method}

`match` 方法会返回字符串中与给定正则表达式模式相匹配的部分：

```php
use Illuminate\Support\Str;

$result = Str::of('foo bar')->match('/bar/');

// 'bar'

$result = Str::of('foo bar')->match('/foo (.*)/');

// 'bar'
```



#### `matchAll` {.collection-method}

`matchAll` 方法将返回一个集合，其中包含字符串中与给定正则表达式模式匹配的部分：

```php
use Illuminate\Support\Str;

$result = Str::of('bar foo bar')->matchAll('/bar/');

// collect(['bar', 'bar'])
```

如果你在表达式中指定了一个匹配分组，Laravel 将返回一个集合，集合中包含**第一个匹配分组**的所有匹配结果：

```php
use Illuminate\Support\Str;

$result = Str::of('bar fun bar fly')->matchAll('/f(\w*)/');

// collect(['un', 'ly']);
```

如果没有找到任何匹配项，将返回一个空集合。

#### `isMatch` {.collection-method}

`isMatch` 方法用于判断字符串是否匹配给定的正则表达式，如果匹配则返回 `true`：

```php
use Illuminate\Support\Str;

$result = Str::of('foo bar')->isMatch('/foo (.*)/');

// true

$result = Str::of('laravel')->isMatch('/foo (.*)/');

// false
```

#### `newLine` {.collection-method}

`newLine` 方法会在字符串末尾追加一个“行结束”字符：

```php
use Illuminate\Support\Str;

$padded = Str::of('Laravel')->newLine()->append('Framework');

// 'Laravel
//  Framework'
```

#### `padBoth` {.collection-method}

`padBoth` 方法是对 PHP `str_pad` 函数的封装，它会在字符串**两侧**使用另一个字符串进行填充，直到最终字符串达到指定长度：

```php
use Illuminate\Support\Str;

$padded = Str::of('James')->padBoth(10, '_');

// '__James___'

$padded = Str::of('James')->padBoth(10);

// '  James   '
```

#### `padLeft` {.collection-method}

`padLeft` 方法是对 PHP `str_pad` 函数的封装，它会在字符串**左侧**使用另一个字符串进行填充，直到最终字符串达到指定长度：

```php
use Illuminate\Support\Str;

$padded = Str::of('James')->padLeft(10, '-=');

// '-=-=-James'

$padded = Str::of('James')->padLeft(10);

// '     James'
```



#### `padRight` {.collection-method}

`padRight` 方法是对 PHP 的 `str_pad` 函数的封装，它会在字符串的**右侧**使用另一个字符串进行填充，直到最终字符串达到期望的长度：

```php
use Illuminate\Support\Str;

$padded = Str::of('James')->padRight(10, '-');

// 'James-----'

$padded = Str::of('James')->padRight(10);

// 'James     '
```

#### `pipe` {.collection-method}

`pipe` 方法允许你通过将字符串的当前值传递给指定的可调用对象（callable）来对字符串进行转换：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$hash = Str::of('Laravel')->pipe('md5')->prepend('Checksum: ');

// 'Checksum: a5c95b86291ea299fcbe64458ed12702'

$closure = Str::of('foo')->pipe(function (Stringable $str) {
    return 'bar';
});

// 'bar'
```

#### `plural` {.collection-method}

`plural` 方法会将一个单数单词字符串转换为其复数形式。该函数支持 [Laravel 复数转换器所支持的任意语言](/docs/laravel/12.x/localization#pluralization-language)

```php
use Illuminate\Support\Str;

$plural = Str::of('car')->plural();

// cars

$plural = Str::of('child')->plural();

// children
```

你可以向该方法传入一个整数作为第二个参数，用于获取字符串的单数或复数形式：

```php
use Illuminate\Support\Str;

$plural = Str::of('child')->plural(2);

// children

$plural = Str::of('child')->plural(1);

// child
```

#### `position` {.collection-method}

`position` 方法会返回子字符串在字符串中**首次出现的位置**。如果该子字符串在字符串中不存在，则返回 `false`：

```php
use Illuminate\Support\Str;

$position = Str::of('Hello, World!')->position('Hello');

// 0

$position = Str::of('Hello, World!')->position('W');

// 7
```



#### `prepend` {.collection-method}

`prepend` 方法会将给定的值**前置**到字符串上：

```php
use Illuminate\Support\Str;

$string = Str::of('Framework')->prepend('Laravel ');

// Laravel Framework
```

#### `remove` {.collection-method}

`remove` 方法会从字符串中移除给定的值或值数组：

```php
use Illuminate\Support\Str;

$string = Str::of('Arkansas is quite beautiful!')->remove('quite');

// Arkansas is beautiful!
```

你也可以将 `false` 作为第二个参数传入，以在移除字符串时忽略大小写。

#### `repeat` {.collection-method}

`repeat` 方法会重复给定的字符串：

```php
use Illuminate\Support\Str;

$repeated = Str::of('a')->repeat(5);

// aaaaa
```

#### `replace` {.collection-method}

`replace` 方法会替换字符串中的给定字符串：

```php
use Illuminate\Support\Str;

$replaced = Str::of('Laravel 6.x')->replace('6.x', '7.x');

// Laravel 7.x
```

`replace` 方法还接受一个 `caseSensitive` 参数。默认情况下，`replace` 方法是区分大小写的：

```php
$replaced = Str::of('macOS 13.x')->replace(
    'macOS', 'iOS', caseSensitive: false
);
```

#### `replaceArray` {.collection-method}

`replaceArray` 方法会使用一个数组，按顺序替换字符串中的给定值：

```php
use Illuminate\Support\Str;

$string = 'The event will take place between ? and ?';

$replaced = Str::of($string)->replaceArray('?', ['8:30', '9:00']);

// The event will take place between 8:30 and 9:00
```

#### `replaceFirst` {.collection-method}

`replaceFirst` 方法会替换字符串中**第一次出现**的给定值：

```php
use Illuminate\Support\Str;

$replaced = Str::of('the quick brown fox jumps over the lazy dog')->replaceFirst('the', 'a');

// a quick brown fox jumps over the lazy dog
```



#### `replaceLast` {.collection-method}

`replaceLast` 方法会替换字符串中**最后一次出现**的给定值：

```php
use Illuminate\Support\Str;

$replaced = Str::of('the quick brown fox jumps over the lazy dog')->replaceLast('the', 'a');

// the quick brown fox jumps over a lazy dog
```

#### `replaceMatches` {.collection-method}

`replaceMatches` 方法会将字符串中**所有**匹配给定模式的部分替换为指定的替换字符串：

```php
use Illuminate\Support\Str;

$replaced = Str::of('(+1) 501-555-1000')->replaceMatches('/[^A-Za-z0-9]++/', '')

// '15015551000'
```

`replaceMatches` 方法还接受一个闭包，该闭包会针对每一段匹配给定模式的字符串被调用，从而允许你在闭包中执行替换逻辑并返回替换后的值：

```php
use Illuminate\Support\Str;

$replaced = Str::of('123')->replaceMatches('/\d/', function (array $matches) {
    return '['.$matches[0].']';
});

// '[1][2][3]'
```

#### `replaceStart` {.collection-method}

`replaceStart` 方法仅在给定值出现在字符串**起始位置**时，才会替换该值的第一次出现：

```php
use Illuminate\Support\Str;

$replaced = Str::of('Hello World')->replaceStart('Hello', 'Laravel');

// Laravel World

$replaced = Str::of('Hello World')->replaceStart('World', 'Laravel');

// Hello World
```

#### `replaceEnd` {.collection-method}

`replaceEnd` 方法仅在给定值出现在字符串**结尾位置**时，才会替换该值的最后一次出现：

```php
use Illuminate\Support\Str;

$replaced = Str::of('Hello World')->replaceEnd('World', 'Laravel');

// Hello Laravel

$replaced = Str::of('Hello World')->replaceEnd('Hello', 'Laravel');

// Hello World
```



#### `scan` {.collection-method}

`scan` 方法会根据 [`sscanf` PHP 函数](https://www.php.net/manual/en/function.sscanf.php) 所支持的格式，从字符串中解析输入并返回一个集合：

```php
use Illuminate\Support\Str;

$collection = Str::of('filename.jpg')->scan('%[^.].%s');

// collect(['filename', 'jpg'])
```

#### `singular` {.collection-method}

`singular` 方法会将字符串转换为其单数形式。该函数支持 [Laravel 复数转换器所支持的任意语言](/docs/laravel/12.x/localization#pluralization-language)：

```php
use Illuminate\Support\Str;

$singular = Str::of('cars')->singular();

// car

$singular = Str::of('children')->singular();

// child
```

#### `slug` {.collection-method}

`slug` 方法会根据给定的字符串生成一个适合用于 URL 的“slug”：

```php
use Illuminate\Support\Str;

$slug = Str::of('Laravel Framework')->slug('-');

// laravel-framework
```

#### `snake` {.collection-method}

`snake` 方法会将给定的字符串转换为 `snake_case` 格式：

```php
use Illuminate\Support\Str;

$converted = Str::of('fooBar')->snake();

// foo_bar
```

#### `split` {.collection-method}

`split` 方法会使用正则表达式将字符串拆分为一个集合：

```php
use Illuminate\Support\Str;

$segments = Str::of('one, two, three')->split('/[\s,]+/');

// collect(["one", "two", "three"])
```

#### `squish` {.collection-method}

`squish` 方法会移除字符串中所有多余的空白字符，包括单词之间的多余空白：

```php
use Illuminate\Support\Str;

$string = Str::of('    laravel    framework    ')->squish();

// laravel framework
```

#### `start` {.collection-method}

`start` 方法会在字符串**尚未以给定值开头时**，为其添加**一个实例**的该值：

```php
use Illuminate\Support\Str;

$adjusted = Str::of('this/string')->start('/');

// /this/string

$adjusted = Str::of('/this/string')->start('/');

// /this/string
```



<a name="method-fluent-str-starts-with"></a>
#### `startsWith` {.collection-method}

`startsWith` 方法判断提供的字符串是否由给定的值开始：

```php
use Illuminate\Support\Str;

$result = Str::of('This is my name')->startsWith('This');

// true
```

<a name="method-fluent-str-strip-tags"></a>
#### `stripTags` {.collection-method}

`stripTags` 方法移除字符串中所有的HTML和PHP标签：

```php
use Illuminate\Support\Str;

$result = Str::of('<a href="https://laravel.com">Taylor <b>Otwell</b></a>')->stripTags();

// Taylor Otwell

$result = Str::of('<a href="https://laravel.com">Taylor <b>Otwell</b></a>')->stripTags('<b>');

// Taylor <b>Otwell</b>
```

<a name="method-fluent-str-studly"></a>
#### `studly` {.collection-method}

`studly`方法将给定的字符串转换成`大驼峰式`：

```php
use Illuminate\Support\Str;

$converted = Str::of('foo_bar')->studly();

// FooBar
```

<a name="method-fluent-str-substr"></a>
#### `substr` {.collection-method}

`substr`方法根据给定的起始位置和长度参数，返回截取的字符串：

```php
use Illuminate\Support\Str;

$string = Str::of('Laravel Framework')->substr(8);

// Framework

$string = Str::of('Laravel Framework')->substr(8, 5);

// Frame
```

<a name="method-fluent-str-substrreplace"></a>
#### `substrReplace` {.collection-method}

`substrReplace`方法根据第二个参数给定的起始位置和第三个参数给定的替换字符数量，将字符串进行部分替换.如果第三个参数传入`0`，子字符串将被插入字符串而不替换原字符串的任何字符：

```php
use Illuminate\Support\Str;

$string = Str::of('1300')->substrReplace(':', 2);

// 13:

$string = Str::of('The Framework')->substrReplace(' Laravel', 3, 0);

// The Laravel Framework
```



#### `swap` {.collection-method}

`swap` 方法使用 PHP 的 `strtr` 函数来**替换字符串中的多个值**：

```php
use Illuminate\Support\Str;

$string = Str::of('Tacos are great!')
    ->swap([
        'Tacos' => 'Burritos',
        'great' => 'fantastic',
    ]);

// Burritos are fantastic!
```

#### `take` {.collection-method}

`take` 方法**从字符串的开头返回指定数量的字符**：

```php
use Illuminate\Support\Str;

$taken = Str::of('Build something amazing!')->take(5);

// Build
```

#### `tap` {.collection-method}

`tap` 方法会将字符串传递给给定的闭包，**允许你在不影响字符串本身的情况下检查和操作它**。
无论闭包中返回什么，`tap` 方法**始终返回原始字符串**：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('Laravel')
    ->append(' Framework')
    ->tap(function (Stringable $string) {
        dump('String after append: '.$string);
    })
    ->upper();

// LARAVEL FRAMEWORK
```

#### `test` {.collection-method}

`test` 方法用于**判断字符串是否匹配给定的正则表达式模式**：

```php
use Illuminate\Support\Str;

$result = Str::of('Laravel Framework')->test('/Laravel/');

// true
```

#### `title` {.collection-method}

`title` 方法会将给定字符串**转换为标题格式（Title Case）**：

```php
use Illuminate\Support\Str;

$converted = Str::of('a nice title uses the correct case')->title();

// A Nice Title Uses The Correct Case
```

#### `toBase64` {.collection-method}

`toBase64` 方法会将给定字符串**转换为 Base64 编码**：

```php
use Illuminate\Support\Str;

$base64 = Str::of('Laravel')->toBase64();

// TGFyYXZlbA==
```



#### `toHtmlString` {.collection-method}

`toHtmlString` 方法会将给定的字符串**转换为 `Illuminate\Support\HtmlString` 的实例**，
在 Blade 模板中渲染时，该字符串**不会被转义**：

```php
use Illuminate\Support\Str;

$htmlString = Str::of('Nuno Maduro')->toHtmlString();
```

#### `toUri` {.collection-method}

`toUri` 方法会将给定的字符串**转换为 [`Illuminate\Support\Uri`](/docs/laravel/12.x/helpers#uri) 的实例**：

```php
use Illuminate\Support\Str;

$uri = Str::of('https://example.com')->toUri();
```

#### `transliterate` {.collection-method}

`transliterate` 方法会尝试将给定的字符串**转换为最接近的 ASCII 表示形式**：

```php
use Illuminate\Support\Str;

$email = Str::of('ⓣⓔⓢⓣ@ⓛⓐⓡⓐⓥⓔⓛ.ⓒⓞⓜ')->transliterate()

// 'test@laravel.com'
```

#### `trim` {.collection-method}

`trim` 方法用于**去除字符串两端的空白字符**。
与 PHP 原生的 `trim` 函数不同，Laravel 的 `trim` 方法**还会移除 Unicode 空白字符**：

```php
use Illuminate\Support\Str;

$string = Str::of('  Laravel  ')->trim();

// 'Laravel'

$string = Str::of('/Laravel/')->trim('/');

// 'Laravel'
```

#### `ltrim` {.collection-method}

`ltrim` 方法用于**去除字符串左侧的空白字符**。
与 PHP 原生的 `ltrim` 函数不同，Laravel 的 `ltrim` 方法**还会移除 Unicode 空白字符**：

```php
use Illuminate\Support\Str;

$string = Str::of('  Laravel  ')->ltrim();

// 'Laravel  '

$string = Str::of('/Laravel/')->ltrim('/');

// 'Laravel/'
```

#### `rtrim` {.collection-method}

`rtrim` 方法用于**去除字符串右侧的空白字符**。
与 PHP 原生的 `rtrim` 函数不同，Laravel 的 `rtrim` 方法**还会移除 Unicode 空白字符**：

```php
use Illuminate\Support\Str;

$string = Str::of('  Laravel  ')->rtrim();

// '  Laravel'

$string = Str::of('/Laravel/')->rtrim('/');

// '/Laravel'
```



<a name="method-fluent-str-ucfirst"></a>
#### `ucfirst` {.collection-method}

`ucfirst` 方法返回首字母大写的给定字符串：

```php
use Illuminate\Support\Str;

$string = Str::of('foo bar')->ucfirst();

// Foo bar
```

<a name="method-fluent-str-ucsplit"></a>
#### `ucsplit` {.collection-method}

`ucsplit` 方法将给定的字符串按大写字符拆分为集合：

```php
use Illuminate\Support\Str;

$string = Str::of('Foo Bar')->ucsplit();

// collect(['Foo', 'Bar'])
```

<a name="method-fluent-str-unwrap"></a>
#### `unwrap` {.collection-method}

`unwrap` 方法从给定字符串的开头和结尾删除指定的字符串：

```php
use Illuminate\Support\Str;

Str::of('-Laravel-')->unwrap('-');

// Laravel

Str::of('{framework: "Laravel"}')->unwrap('{', '}');

// framework: "Laravel"
```

<a name="method-fluent-str-upper"></a>
#### `upper` {.collection-method}

`upper` 方法将给定的字符串转换为大写：

```php
use Illuminate\Support\Str;

$adjusted = Str::of('laravel')->upper();

// LARAVEL
```

<a name="method-fluent-str-when"></a>
#### `when` {.collection-method}

如果给定条件为 `true`，则 `when` 方法调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('Taylor')
    ->when(true, function (Stringable $string) {
        return $string->append(' Otwell');
    });

// 'Taylor Otwell'
```

如果需要，你可以将另一个闭包作为第三个参数传递给 `when` 方法。如果条件参数的结果为 `false` ，将执行此闭包。

<a name="method-fluent-str-when-contains"></a>
#### `whenContains` {.collection-method}

如果字符串包含给定值，则 `whenContains` 方法调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('tony stark')
    ->whenContains('tony', function (Stringable $string) {
        return $string->title();
    });

// 'Tony Stark'
```

如果需要，你可以将另一个闭包作为第三个参数传递给 `when` 方法。如果字符串不包含给定值，则执行此闭包。



您还可以传递一个值数组来检测给定的字符串是否包含数组中的任意值：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('tony stark')
    ->whenContains(['tony', 'hulk'], function (Stringable $string) {
        return $string->title();
    });

// Tony Stark
```

<a name="method-fluent-str-when-contains-all"></a>
#### `whenContainsAll` {.collection-method}

如果字符串包含所有给定的子字符串，则 `whenContainsAll` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('tony stark')
    ->whenContainsAll(['tony', 'stark'], function (Stringable $string) {
        return $string->title();
    });

// 'Tony Stark'
```

如果需要，你可以将另一个闭包作为第三个参数传递给该 `when` 方法。如果条件参数的结果为 `false` ，将执行此闭包。

<a name="method-fluent-str-when-empty"></a>
#### `whenEmpty` {.collection-method}

如果字符串为空，则 `whenEmpty` 方法将调用给定的闭包。如果闭包返回一个值，`whenEmpty` 方法也将返回该值。如果闭包不返回值，则将返回流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('  ')->trim()->whenEmpty(function (Stringable $string) {
    return $string->prepend('Laravel');
});

// 'Laravel'
```

<a name="method-fluent-str-when-not-empty"></a>
#### `whenNotEmpty` {.collection-method}

如果字符串不为空，则 `whenNotEmpty` 方法将调用给定的闭包。如果闭包返回一个值，`whenNotEmpty` 方法也将返回该值。如果闭包不返回值，则将返回流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('Framework')->whenNotEmpty(function (Stringable $string) {
    return $string->prepend('Laravel ');
});

// 'Laravel Framework'
```



<a name="method-fluent-str-when-starts-with"></a>
#### `whenStartsWith` {.collection-method}

如果字符串以给定的子字符串开头，则 `whenStartsWith` 方法调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('disney world')->whenStartsWith('disney', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a name="method-fluent-str-when-ends-with"></a>
#### `whenEndsWith` {.collection-method}

如果字符串以给定的子字符串结尾，则 `whenEndsWith` 方法调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('disney world')->whenEndsWith('world', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a name="method-fluent-str-when-exactly"></a>
#### `whenExactly` {.collection-method}

如果字符串与给定的字符串完全匹配，则 `whenExactly` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('laravel')->whenExactly('laravel', function (Stringable $string) {
    return $string->title();
});

// 'Laravel'
```

<a name="method-fluent-str-when-not-exactly"></a>
#### `whenNotExactly` {.collection-method}

如果字符串与给定的字符串不完全匹配，则 `whenNotExactly` 方法调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('framework')->whenNotExactly('laravel', function (Stringable $string) {
    return $string->title();
});

// 'Framework'
```

<a name="method-fluent-str-when-is"></a>
#### `whenIs` {.collection-method}

如果字符串与给定模式匹配，则 `whenIs` 方法将调用给定的闭包。星号可用作通配符值。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('foo/bar')->whenIs('foo/*', function (Stringable $string) {
    return $string->append('/baz');
});

// 'foo/bar/baz'
```



<a name="method-fluent-str-when-is-ascii"></a>
#### `whenIsAscii` {.collection-method}

如果字符串是 7 位 ASCII，则 `whenIsAscii` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('laravel')->whenIsAscii(function (Stringable $string) {
    return $string->title();
});

// 'Laravel'
```

<a name="method-fluent-str-when-is-ulid"></a>
#### `whenIsUlid` {.collection-method}

如果字符串是有效的 ULID，则 `whenIsUlid` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;

$string = Str::of('01gd6r360bp37zj17nxb55yv40')->whenIsUlid(function (Stringable $string) {
    return $string->substr(0, 8);
});

// '01gd6r36'
```

<a name="method-fluent-str-when-is-uuid"></a>
#### `whenIsUuid` {.collection-method}

如果字符串是有效的 UUID，则 `whenIsUuid` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('a0a2a2d2-0b87-4a18-83f2-2529882be2de')->whenIsUuid(function (Stringable $string) {
    return $string->substr(0, 8);
});

// 'a0a2a2d2'
```

<a name="method-fluent-str-when-test"></a>
#### `whenTest` {.collection-method}

如果字符串与给定的正则表达式匹配，则 `whenTest` 方法将调用给定的闭包。闭包将接收流畅的字符串实例：

```php
use Illuminate\Support\Str;
use Illuminate\Support\Stringable;

$string = Str::of('laravel framework')->whenTest('/laravel/', function (Stringable $string) {
    return $string->title();
});

// 'Laravel Framework'
```

<a name="method-fluent-str-word-count"></a>
#### `wordCount` {.collection-method}

`wordCount` 方法返回字符串包含的单词数：

```php
use Illuminate\Support\Str;

Str::of('Hello, world!')->wordCount(); // 2
```



<a name="method-fluent-str-words"></a>
#### `words` {.collection-method}

`words` 方法限制字符串中的单词数。如果有必要，你可以指定一个额外的字符串，它将被追加到被截断的字符串上：
```php
use Illuminate\Support\Str;

$string = Str::of('Perfectly balanced, as all things should be.')->words(3, ' >>>');

// Perfectly balanced, as >>>
```

<a name="method-fluent-str-wrap"></a>
#### `wrap` {.collection-method}

`wrap` 方法用一个额外的字符串或字符串对包装给定的字符串：

```php
use Illuminate\Support\Str;

Str::of('Laravel')->wrap('"');

// "Laravel"

Str::is('is')->wrap(before: 'This ', after: ' Laravel!');

// This is Laravel!
```
