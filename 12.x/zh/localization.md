
# 本地化

- [简介](#introduction)
 - [发布语言文件](#publishing-the-language-files)
 - [配置语言环境](#configuring-the-locale)
 - [复数化语言](#pluralization-language)
- [定义翻译字符串](#defining-translation-strings)
 - [使用短键](#using-short-keys)
 - [使用翻译字符串作为键](#using-translation-strings-as-keys)
- [获取翻译字符串](#retrieving-translation-strings)
  - [在翻译字符串中替换参数](#replacing-parameters-in-translation-strings)
  - [复数化](#pluralization)
- [覆盖包语言文件](#overriding-package-language-files)

## 简介

> [!笔记]
> 默认情况下，Laravel 应用程序骨架并不包含 `lang` 目录。
如果你想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

Laravel 的本地化功能提供了一种方便的方法来获取不同语言的字符串，使你能够轻松地在应用程序中支持多种语言。

Laravel 提供了两种方式来管理翻译字符串。首先，语言字符串可以存储在应用程序的 `lang` 目录中的文件中。在该目录中，每种应用程序支持的语言可能都有一个子目录。这是 Laravel 用于管理内置功能（如验证错误消息）翻译字符串的方式，例如：

```text
/lang
    /en
        messages.php
    /es
        messages.php
```

或者，翻译字符串可以定义在放置于 `lang` 目录中的 JSON 文件中。采用这种方式时，应用程序支持的每种语言在该目录中都会有一个对应的 JSON 文件。对于拥有大量可翻译字符串的应用程序，推荐采用这种方式：

```text
/lang
    en.json
    es.json
```

我们将在本文档中讨论这两种管理翻译字符串的方法。

### 发布语言文件

默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果你想自定义 Laravel 的语言文件或创建自己的语言文件，你应该通过 `lang:publish` Artisan 命令生成 `lang` 目录。`lang:publish` 命令将在你的应用程序中创建 `lang` 目录，并发布 Laravel 使用的默认语言文件集：

```shell
php artisan lang:publish
```



### 配置语言环境

应用程序的默认语言存储在 `config/app.php` 配置文件的 `locale` 配置项中，该配置项通常通过 `APP_LOCALE` 环境变量进行设置。你可以自由修改此值以满足应用程序的需求。

你还可以配置一个“备用语言”，当默认语言中没有某个翻译字符串时将使用该备用语言。与默认语言一样，备用语言也在 `config/app.php` 配置文件中进行配置，其值通常通过 `APP_FALLBACK_LOCALE` 环境变量进行设置。

你可以在运行时使用 `App` 外观（facade）提供的 `setLocale` 方法，为单个 HTTP 请求修改默认语言：

```php
use Illuminate\Support\Facades\App;

Route::get('/greeting/{locale}', function (string $locale) {
    if (! in_array($locale, ['en', 'es', 'fr'])) {
        abort(400);
    }

    App::setLocale($locale);

    // ...
});
```

#### 确定当前语言环境

你可以使用 `App` 外观上的 `currentLocale` 和 `isLocale` 方法来确定当前的语言环境，或检查语言环境是否为指定值：

```php
use Illuminate\Support\Facades\App;

$locale = App::currentLocale();

if (App::isLocale('en')) {
    // ...
}
```

### 复数化语言

你可以指示 Laravel 的“复数化器”（pluralizer）使用除英语以外的语言。复数化器被 Eloquent 以及框架的其他部分用来将单数字符串转换为复数字符串。
你可以在应用程序某个服务提供者的 `boot` 方法中调用 `useLanguage` 方法来实现这一点。当前复数化器支持的语言有：`french`、`norwegian-bokmal`、`portuguese`、`spanish` 和 `turkish`：

```php
use Illuminate\Support\Pluralizer;

/**
 * 启动任何应用程序服务
 */
public function boot(): void
{
    Pluralizer::useLanguage('spanish');

    // ...
}
```

> [!警告]
> 如果你自定义了复数化器的语言，应显式定义 Eloquent 模型的[数据表名称](/docs/laravel/12.x/eloquent#table-names)。



## 定义翻译字符串

### 使用短键

通常，翻译字符串存储在 `lang` 目录下的文件中。该目录中应该为应用程序支持的每种语言创建一个子目录。
Laravel 内置功能（如验证错误消息）的翻译字符串管理也是采用这种方式：

```text
/lang
    /en
        messages.php
    /es
        messages.php
```

所有语言文件都返回一个带有键值对的数组。例如：

```php
<?php

// lang/en/messages.php

return [
    'welcome' => 'Welcome to our application!',
];
```

> [!警告]
> > 对于因地区不同而有所差异的语言，你应该按照 **ISO 15897** 命名语言目录。例如，英国英语应命名为 `en_GB` 而不是 `en-gb`。

### 使用翻译字符串作为键

对于拥有大量可翻译字符串的应用来说，给每个字符串都定义一个“短键”在视图中引用时会变得混乱，而且不断为每个翻译字符串想新的键也很繁琐。

因此，Laravel 也支持使用该字符串的“默认”翻译作为键来定义翻译字符串。
使用字符串作为键的语言文件以 **JSON 文件** 的形式存储在 `lang` 目录中。

例如，如果你的应用有西班牙语翻译，你应该创建一个 `lang/es.json` 文件：

```json
{
    "I love programming.": "Me encanta programar."
}
```

#### 键 / 文件冲突

不要定义与其他翻译文件名冲突的翻译字符串键。
例如，如果你在 “NL” 语言环境中翻译 `__('Action')`，而同时存在 `nl/action.php` 文件但不存在 `nl.json` 文件，那么翻译器会返回 `nl/action.php` 文件的全部内容。



## 获取翻译字符串

你可以使用 `__` 辅助函数从语言文件中获取翻译字符串。
如果你使用“短键”来定义翻译字符串，你应该将包含键的文件和键本身传递给 `__` 函数，使用“点”语法。例如，从 `lang/en/messages.php` 文件中获取 `welcome` 翻译字符串：

```php
echo __('messages.welcome');
```

如果指定的翻译字符串不存在，`__` 函数会返回传入的翻译字符串键。因此，上例中如果翻译字符串不存在，`__` 函数将返回 `messages.welcome`。

如果你使用 [默认翻译字符串作为翻译键](#using-translation-strings-as-keys)，你应该将字符串的默认翻译传给 `__` 函数：

```php
echo __('I love programming.');
```

同样，如果翻译字符串不存在，`__` 函数会返回它接收到的翻译字符串键。

如果你使用 [Blade 模板引擎](/docs/laravel/12.x/blade)，你可以使用 `{{ }}` 输出语法来显示翻译字符串：

```blade
{{ __('messages.welcome') }}
```

### 在翻译字符串中替换参数

你可以在翻译字符串中定义占位符，所有占位符都以 `:` 为前缀。例如，你可以定义一个包含名字占位符的欢迎消息：

```php
'welcome' => 'Welcome, :name',
```

在获取翻译字符串时，你可以将一个替换数组作为 `__` 函数的第二个参数来替换占位符：

```php
echo __('messages.welcome', ['name' => 'dayle']);
```



如果你的占位符是全大写，或者只有首字母大写，翻译后的值也会相应地进行大小写处理：

```php
'welcome' => 'Welcome, :NAME', // Welcome, DAYLE
'goodbye' => 'Goodbye, :Name', // Goodbye, Dayle
```

#### 对象占位符的格式化

如果你尝试将一个对象作为翻译占位符，Laravel 会调用该对象的 `__toString` 方法。
[`__toString`](https://www.php.net/manual/en/language.oop5.magic.php#object.tostring) 方法是 PHP 内置的“魔术方法”之一。然而，有时候你可能无法控制某个类的 `__toString` 方法，比如该类属于第三方库时。

在这种情况下，Laravel 允许你为特定类型的对象注册自定义格式化处理器。
要实现这一点，你应调用翻译器的 `stringable` 方法。`stringable` 方法接受一个闭包，并在闭包中类型提示该对象的类型，说明你负责如何格式化它。通常，`stringable` 方法应在应用的 `AppServiceProvider` 类的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Lang;
use Money\Money;

/**
 * 启动应用服务
 */
public function boot(): void
{
    Lang::stringable(function (Money $money) {
        return $money->formatTo('en_GB');
    });
}
```

### 复数化

复数化是一个复杂的问题，因为不同语言的复数规则各不相同；但是 Laravel 可以帮助你根据自定义的复数规则翻译字符串。
使用 `|` 符号，你可以区分字符串的单数和复数形式

```php
'apples' => 'There is one apple|There are many apples',
```



当然，当使用 [将翻译字符串作为键](#using-translation-strings-as-keys) 时，也支持复数化：

```json
{
    "There is one apple|There are many apples": "Hay una manzana|Hay muchas manzanas"
}
```

你甚至可以创建更复杂的复数规则，为多个值区间指定翻译字符串：

```php
'apples' => '{0} There are none|[1,19] There are some|[20,*] There are many',
```

在定义了带复数选项的翻译字符串后，你可以使用 `trans_choice` 函数来根据给定的“计数”获取对应的翻译行。在这个例子中，因为计数大于 1，返回的是复数形式的翻译字符串：

```php
echo trans_choice('messages.apples', 10);
```

你也可以在复数字符串中定义占位符。通过将占位符数组作为 `trans_choice` 函数的第三个参数传入，可以替换这些占位符：

```php
'minutes_ago' => '{1} :value minute ago|[2,*] :value minutes ago',

echo trans_choice('time.minutes_ago', 5, ['value' => 5]);
```

如果你希望显示传递给 `trans_choice` 函数的整数值，可以使用内置的 `:count` 占位符：

```php
'apples' => '{0} There are none|{1} There is one|[2,*] There are :count',
```

## 覆盖包语言文件


有些包可能会自带自己的语言文件。你无需修改包的核心文件来调整这些翻译行，而是可以通过将文件放置在 `lang/vendor/{package}/{locale}` 目录下进行覆盖。
例如，如果你需要覆盖包 `skyrim/hearthfire` 中 `messages.php` 的英文翻译字符串，应将语言文件放置在：`lang/vendor/hearthfire/en/messages.php`。在这个文件中，你只需定义你希望覆盖的翻译字符串。未覆盖的翻译字符串仍然会从包原始语言文件中加载。
