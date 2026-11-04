
# Prompts

-   [介绍](#introduction)
-   [安装](#installation)
-   [可用的 Prompts](#available-prompts)
    -   [Text](#text)
    -   [Textarea](#textarea)
    -   [Password](#password)
    -   [Confirm](#confirm)
    -   [Select](#select)
    -   [Multi-select](#multiselect)
    -   [Suggest](#suggest)
    -   [Search](#search)
    -   [Multi-search](#multisearch)
    -   [Pause](#pause)
-   [在验证之前转换输入](#transforming-input-before-validation)
-   [表单](#forms)
-   [信息提示](#informational-messages)
-   [表格](#tables)
-   [旋转动画](#spin)
-   [进度条](#progress)
-   [清屏](#clear)
-   [终端注意事项](#terminal-considerations)
-   [不支持的环境与回退方案](#fallbacks)

## 介绍

[Laravel Prompts](https://github.com/laravel/prompts) 是一个 PHP 包，用于在命令行应用程序中添加美观且用户友好的表单，具备类似浏览器的功能，包括占位符文本和验证。

<img src="https://laravel.com/img/docs/prompts-example.png">

Laravel Prompts 非常适合在你的 [Artisan 控制台命令](/docs/laravel/12.x/artisan#writing-commands) 中接受用户输入，但它也可以用于任何命令行 PHP 项目。

> [!注意]
> Laravel Prompts 支持 macOS、Linux 和带 WSL 的 Windows。更多信息请参阅我们关于[不支持的环境与回退方案](#fallbacks)的文档。


## 安装

Laravel Prompts 已经包含在 Laravel 的最新版本中。

你也可以在其他 PHP 项目中使用 Composer 包管理器进行安装：


```shell
composer require laravel/prompts
```

## 可用的 Prompts (Available Prompts)

### Text

`text` 函数会向用户提出给定问题，接收输入，然后返回它：

```php
use function Laravel\Prompts\text;

$name = text('What is your name?');
```



你也可以包含占位符文本、默认值以及提示信息：

```php
$name = text(
    label: 'What is your name?',
    placeholder: 'E.g. Taylor Otwell',
    default: $user?->name,
    hint: 'This will be displayed on your profile.'
);
```

#### 必填值 (Required Values)

如果你需要强制输入一个值，可以传递 `required` 参数：

```php
$name = text(
    label: 'What is your name?',
    required: true
);
```

如果你想自定义验证消息，你也可以传递一个字符串：

```php
$name = text(
    label: 'What is your name?',
    required: 'Your name is required.'
);
```

#### 额外验证

最后，如果你想执行额外的验证逻辑，可以将一个闭包传递给 `validate` 参数：

```php
$name = text(
    label: 'What is your name?',
    validate: fn (string $value) => match (true) {
        strlen($value) < 3 => 'The name must be at least 3 characters.',
        strlen($value) > 255 => 'The name must not exceed 255 characters.',
        default => null
    }
);
```

该闭包会接收输入的值，并可以返回一条错误消息；如果验证通过，则返回 `null`。

或者，你也可以利用 Laravel 的 [验证器](/docs/laravel/12.x/validation)。
要做到这一点，只需为 `validate` 参数提供一个数组，数组包含属性名和所需的验证规则：

```php
$name = text(
    label: 'What is your name?',
    validate: ['name' => 'required|max:255|unique:users']
);
```

### Textarea

`textarea` 函数会向用户提出给定问题，接收其通过多行文本输入的内容，并返回：

```php
use function Laravel\Prompts\textarea;

$story = textarea('Tell me a story.');
```

你也可以包含占位符文本、默认值以及提示信息：

```php
$story = textarea(
    label: 'Tell me a story.',
    placeholder: 'This is a story about...',
    hint: 'This will be displayed on your profile.'
);
```



#### 必填值

如果你需要强制输入一个值，可以传递 `required` 参数：

```php
$story = textarea(
    label: 'Tell me a story.',
    required: true
);
```

如果你想自定义验证消息，你也可以传递一个字符串：

```php
$story = textarea(
    label: 'Tell me a story.',
    required: 'A story is required.'
);
```

#### 额外验证

最后，如果你想执行额外的验证逻辑，可以将一个闭包传递给 `validate` 参数：

```php
$story = textarea(
    label: 'Tell me a story.',
    validate: fn (string $value) => match (true) {
        strlen($value) < 250 => 'The story must be at least 250 characters.',
        strlen($value) > 10000 => 'The story must not exceed 10,000 characters.',
        default => null
    }
);
```

该闭包会接收输入的值，并可以返回一条错误消息；如果验证通过，则返回 `null`。

或者，你也可以利用 Laravel 的 [验证器](/docs/laravel/12.x/validation)。
要做到这一点，只需为 `validate` 参数提供一个数组，数组包含属性名和所需的验证规则：

```php
$story = textarea(
    label: 'Tell me a story.',
    validate: ['story' => 'required|max:10000']
);
```

### 密码

`password` 函数与 `text` 函数类似，但用户在控制台中输入时，其输入内容会被隐藏。
这在询问密码等敏感信息时非常有用：

```php
use function Laravel\Prompts\password;

$password = password('What is your password?');
```

你也可以包含占位符文本和提示信息：

```php
$password = password(
    label: 'What is your password?',
    placeholder: 'password',
    hint: 'Minimum 8 characters.'
);
```



#### 必填值

如果你需要强制输入一个值，可以传递 `required` 参数：

```php
$password = password(
    label: 'What is your password?',
    required: true
);
```

如果你想自定义验证消息，你也可以传递一个字符串：

```php
$password = password(
    label: 'What is your password?',
    required: 'The password is required.'
);
```

#### 额外验证

最后，如果你想执行额外的验证逻辑，可以将一个闭包传递给 `validate` 参数：

```php
$password = password(
    label: 'What is your password?',
    validate: fn (string $value) => match (true) {
        strlen($value) < 8 => 'The password must be at least 8 characters.',
        default => null
    }
);
```

该闭包会接收输入的值，并可以返回一条错误消息；如果验证通过，则返回 `null`。

或者，你也可以利用 Laravel 的 [验证器](/docs/laravel/12.x/validation)。
要做到这一点，只需为 `validate` 参数提供一个数组，数组包含属性名和所需的验证规则：

```php
$password = password(
    label: 'What is your password?',
    validate: ['password' => 'min:8']
);
```

### 确认

如果你需要向用户询问一个 “是/否” 确认，你可以使用 `confirm` 函数。
用户可以使用方向键，或直接按 `y` 或 `n` 来选择他们的回答。
此函数将返回 `true` 或 `false`。

```php
use function Laravel\Prompts\confirm;

$confirmed = confirm('Do you accept the terms?');
```

你也可以包含一个默认值、对 “Yes” 和 “No” 标签的自定义文字，以及提示信息：

```php
$confirmed = confirm(
    label: 'Do you accept the terms?',
    default: false,
    yes: 'I accept',
    no: 'I decline',
    hint: 'The terms must be accepted to continue.'
);
```



#### 强制选择 “Yes”

如有必要，你可以通过传递 `required` 参数来强制用户选择 “Yes”：

```php
$confirmed = confirm(
    label: 'Do you accept the terms?',
    required: true
);
```

如果你想自定义验证消息，也可以传递一个字符串：

```php
$confirmed = confirm(
    label: 'Do you accept the terms?',
    required: 'You must accept the terms to continue.'
);
```

### 选择

如果你需要用户从预定义的选项中选择，可以使用 `select` 函数：

```php
use function Laravel\Prompts\select;

$role = select(
    label: 'What role should the user have?',
    options: ['Member', 'Contributor', 'Owner']
);
```

你也可以指定默认选项和提示信息：

```php
$role = select(
    label: 'What role should the user have?',
    options: ['Member', 'Contributor', 'Owner'],
    default: 'Owner',
    hint: 'The role may be changed at any time.'
);
```

你还可以向 `options` 参数传递一个关联数组，以便返回被选中的键而不是值：

```php
$role = select(
    label: 'What role should the user have?',
    options: [
        'member' => 'Member',
        'contributor' => 'Contributor',
        'owner' => 'Owner',
    ],
    default: 'owner'
);
```

在列表开始滚动之前，会显示最多五个选项。你可以通过传递 `scroll` 参数来自定义此数量：

```php
$role = select(
    label: 'Which category would you like to assign?',
    options: Category::pluck('name', 'id'),
    scroll: 10
);
```

#### 额外验证

与其他 prompt 函数不同，`select` 函数不接受 `required` 参数，因为不可能什么都不选。
但是，如果你需要提供一个选项但又想阻止它被选中，你可以向 `validate` 参数传递一个闭包：

```php
$role = select(
    label: 'What role should the user have?',
    options: [
        'member' => 'Member',
        'contributor' => 'Contributor',
        'owner' => 'Owner',
    ],
    validate: fn (string $value) =>
        $value === 'owner' && User::where('role', 'owner')->exists()
            ? 'An owner already exists.'
            : null
);
```



如果 `options` 参数是一个关联数组，那么闭包将接收被选中的键，否则将接收被选中的值。
闭包可以返回一条错误消息；如果验证通过，则返回 `null`。

### 多选

如果你需要用户能够选择多个选项，可以使用 `multiselect` 函数：

```php
use function Laravel\Prompts\multiselect;

$permissions = multiselect(
    label: 'What permissions should be assigned?',
    options: ['Read', 'Create', 'Update', 'Delete']
);
```

你也可以指定默认选项和提示信息：

```php
use function Laravel\Prompts\multiselect;

$permissions = multiselect(
    label: 'What permissions should be assigned?',
    options: ['Read', 'Create', 'Update', 'Delete'],
    default: ['Read', 'Create'],
    hint: 'Permissions may be updated at any time.'
);
```

你还可以向 `options` 参数传递一个关联数组，以便返回所选选项的键而不是值：

```php
$permissions = multiselect(
    label: 'What permissions should be assigned?',
    options: [
        'read' => 'Read',
        'create' => 'Create',
        'update' => 'Update',
        'delete' => 'Delete',
    ],
    default: ['read', 'create']
);
```

在列表开始滚动之前，会显示最多五个选项。
你可以通过传递 `scroll` 参数来自定义此数量：

```php
$categories = multiselect(
    label: 'What categories should be assigned?',
    options: Category::pluck('name', 'id'),
    scroll: 10
);
```

#### 强制选择

默认情况下，用户可以选择零个或多个选项。
你可以传递 `required` 参数来强制选择一个或多个选项：

```php
$categories = multiselect(
    label: 'What categories should be assigned?',
    options: Category::pluck('name', 'id'),
    required: true
);
```

如果你想自定义验证消息，可以为 `required` 参数提供一个字符串：

```php
$categories = multiselect(
    label: 'What categories should be assigned?',
    options: Category::pluck('name', 'id'),
    required: 'You must select at least one category'
);
```



#### 额外验证

如果你需要提供一个选项但又想阻止它被选中，可以将闭包传递给 `validate` 参数：

```php
$permissions = multiselect(
    label: 'What permissions should the user have?',
    options: [
        'read' => 'Read',
        'create' => 'Create',
        'update' => 'Update',
        'delete' => 'Delete',
    ],
    validate: fn (array $values) => ! in_array('read', $values)
        ? 'All users require the read permission.'
        : null
);
```

如果 `options` 参数是一个关联数组，则闭包将接收被选中的键，否则将接收被选中的值。
闭包可以返回一条错误消息；如果验证通过，则返回 `null`。

### 自动提示

`suggest` 函数可以用于为可能的选项提供自动补全。
用户仍然可以输入任意答案，无论是否有自动补全提示

```php
use function Laravel\Prompts\suggest;

$name = suggest('What is your name?', ['Taylor', 'Dayle']);
```

或者，你可以向 `suggest` 函数的第二个参数传递一个闭包。
每当用户输入一个字符时，该闭包都会被调用。
闭包应接收一个字符串参数，表示用户目前输入的内容，并返回一个用于自动补全的选项数组：

```php
$name = suggest(
    label: 'What is your name?',
    options: fn ($value) => collect(['Taylor', 'Dayle'])
        ->filter(fn ($name) => Str::contains($name, $value, ignoreCase: true))
)
```

你也可以包含占位符文本、默认值以及提示信息：

```php
$name = suggest(
    label: 'What is your name?',
    options: ['Taylor', 'Dayle'],
    placeholder: 'E.g. Taylor',
    default: $user?->name,
    hint: 'This will be displayed on your profile.'
);
```



#### 必填值

如果你需要用户必须输入一个值，可以传递 `required` 参数：

```php
$name = suggest(
    label: 'What is your name?',
    options: ['Taylor', 'Dayle'],
    required: true
);
```

如果你想自定义验证消息，也可以传递一个字符串：

```php
$name = suggest(
    label: 'What is your name?',
    options: ['Taylor', 'Dayle'],
    required: 'Your name is required.'
);
```

#### 额外验证

最后，如果你想执行额外的验证逻辑，可以将一个闭包传递给 `validate` 参数：

```php
$name = suggest(
    label: 'What is your name?',
    options: ['Taylor', 'Dayle'],
    validate: fn (string $value) => match (true) {
        strlen($value) < 3 => 'The name must be at least 3 characters.',
        strlen($value) > 255 => 'The name must not exceed 255 characters.',
        default => null
    }
);
```

闭包会接收到输入的值，并可以返回一条错误消息，或者在验证通过时返回 `null`。

另外，你也可以利用 Laravel 的 [验证器](/docs/laravel/12.x/validation)。要做到这一点，可以向 `validate` 参数提供一个数组，包含属性名称和所需的验证规则：

```php
$name = suggest(
    label: 'What is your name?',
    options: ['Taylor', 'Dayle'],
    validate: ['name' => 'required|min:3|max:255']
);
```

### 搜索

如果你有大量选项需要用户选择，可以使用 `search` 函数。它允许用户输入查询以过滤结果，然后再使用方向键选择一个选项：

```php
use function Laravel\Prompts\search;

$id = search(
    label: 'Search for the user that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : []
);
```



闭包会接收到用户当前已经输入的文本，并且必须返回一个选项数组。
如果你返回的是一个 **关联数组**，那么最终返回的是被选中选项的 **键**；
否则，会返回被选中选项的 **值**。

当你在过滤数组并打算返回值时，应使用 `array_values` 函数或者集合的 `values` 方法，来确保数组不会变成关联数组：

```php
$names = collect(['Taylor', 'Abigail']);

$selected = search(
    label: 'Search for the user that should receive the mail',
    options: fn (string $value) => $names
        ->filter(fn ($name) => Str::contains($name, $value, ignoreCase: true))
        ->values()
        ->all(),
);
```

你还可以包含占位符文本以及提示信息：

```php
$id = search(
    label: 'Search for the user that should receive the mail',
    placeholder: 'E.g. Taylor Otwell',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    hint: 'The user will receive an email immediately.'
);
```

最多会显示 **5 个选项**，之后列表会开始滚动。
你可以通过传递 `scroll` 参数自定义：

```php
$id = search(
    label: 'Search for the user that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    scroll: 10
);
```

#### 额外验证

如果你希望执行额外的验证逻辑，可以将闭包传递给 `validate` 参数：

```php
$id = search(
    label: 'Search for the user that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    validate: function (int|string $value) {
        $user = User::findOrFail($value);

        if ($user->opted_out) {
            return 'This user has opted-out of receiving mail.';
        }
    }
);
```



如果 `options` 闭包返回的是一个 **关联数组**，那么闭包会接收到被选中的 **键**；否则，它会接收到被选中的 **值**。闭包可以返回一条错误消息，或者在验证通过时返回 `null`。

### 多重搜索

如果你有大量可搜索的选项，并且需要用户能够选择多个项目，`multisearch` 函数允许用户输入搜索查询来过滤结果，然后使用方向键和空格键来选择选项：

```php
use function Laravel\Prompts\multisearch;

$ids = multisearch(
    'Search for the users that should receive the mail',
    fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : []
);
```

闭包会接收到用户当前输入的文本，并且必须返回一个选项数组。
如果你返回的是 **关联数组**，那么会返回所选选项的 **键**；否则，会返回它们的 **值**。

当你在过滤数组并打算返回值时，应使用 `array_values` 函数或者集合的 `values` 方法，确保数组不会变成关联数组：

```php
$names = collect(['Taylor', 'Abigail']);

$selected = multisearch(
    label: 'Search for the users that should receive the mail',
    options: fn (string $value) => $names
        ->filter(fn ($name) => Str::contains($name, $value, ignoreCase: true))
        ->values()
        ->all(),
);
```

你还可以包含占位符文本以及提示信息：

```php
$ids = multisearch(
    label: 'Search for the users that should receive the mail',
    placeholder: 'E.g. Taylor Otwell',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    hint: 'The user will receive an email immediately.'
);
```



在列表开始滚动之前，最多会显示 **5 个选项**。
你可以通过提供 `scroll` 参数进行自定义：

```php
$ids = multisearch(
    label: 'Search for the users that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    scroll: 10
);
```

#### 必填值

默认情况下，用户可以选择 **零个或多个选项**。
你可以传递 `required` 参数来强制要求选择一个或多个选项：

```php
$ids = multisearch(
    label: 'Search for the users that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    required: true
);
```

如果你想自定义验证消息，也可以将字符串传递给 `required` 参数：

```php
$ids = multisearch(
    label: 'Search for the users that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    required: 'You must select at least one user.'
);
```

#### 额外验证

如果你希望执行额外的验证逻辑，可以将闭包传递给 `validate` 参数：

```php
$ids = multisearch(
    label: 'Search for the users that should receive the mail',
    options: fn (string $value) => strlen($value) > 0
        ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
        : [],
    validate: function (array $values) {
        $optedOut = User::whereLike('name', '%a%')->findMany($values);

        if ($optedOut->isNotEmpty()) {
            return $optedOut->pluck('name')->join(', ', ', and ').' have opted out.';
        }
    }
);
```



如果 `options` 闭包返回一个关联数组，那么闭包将接收所选的键；否则，它将接收所选的值。闭包可以返回一条错误消息，或者在验证通过时返回 `null`。

### 暂停

`pause` 函数可用于向用户显示提示信息，并等待用户按下 Enter / Return 键以确认是否继续：

```php
use function Laravel\Prompts\pause;

pause('Press ENTER to continue.');
```

## 在验证前转换输入

有时，你可能希望在验证之前转换提示输入。例如，你可能希望去除输入字符串中的空白。为此，许多提示函数都提供了一个 `transform` 参数，它接受一个闭包：

```php
$name = text(
    label: 'What is your name?',
    transform: fn (string $value) => trim($value),
    validate: fn (string $value) => match (true) {
        strlen($value) < 3 => 'The name must be at least 3 characters.',
        strlen($value) > 255 => 'The name must not exceed 255 characters.',
        default => null
    }
);
```

## 表单

通常，你会有多个提示需要依次显示，以便在执行进一步操作之前收集信息。你可以使用 `form` 函数来创建一组分组的提示，供用户填写：

```php
use function Laravel\Prompts\form;

$responses = form()
    ->text('What is your name?', required: true)
    ->password('What is your password?', validate: ['password' => 'min:8'])
    ->confirm('Do you accept the terms?')
    ->submit();
```



`submit` 方法会返回一个数字索引数组，其中包含来自表单提示的所有响应。不过，你也可以通过 `name` 参数为每个提示指定一个名称。当提供了名称后，就可以通过该名称来访问对应提示的响应：

```php
use App\Models\User;
use function Laravel\Prompts\form;

$responses = form()
    ->text('What is your name?', required: true, name: 'name')
    ->password(
        label: 'What is your password?',
        validate: ['password' => 'min:8'],
        name: 'password'
    )
    ->confirm('Do you accept the terms?')
    ->submit();

User::create([
    'name' => $responses['name'],
    'password' => $responses['password'],
]);
```

使用 `form` 函数的主要好处是，用户可以通过 `CTRL + U` 返回表单中的上一个提示。这让用户能够修正错误或修改选择，而无需取消并重新开始整个表单。

如果你需要对表单中的提示进行更细粒度的控制，可以使用 `add` 方法，而不是直接调用某个提示函数。`add` 方法会接收用户之前提供的所有响应：

```php
use function Laravel\Prompts\form;
use function Laravel\Prompts\outro;
use function Laravel\Prompts\text;

$responses = form()
    ->text('What is your name?', required: true, name: 'name')
    ->add(function ($responses) {
        return text("How old are you, {$responses['name']}?");
    }, name: 'age')
    ->submit();

outro("Your name is {$responses['name']} and you are {$responses['age']} years old.");
```

## 信息提示

`note`、`info`、`warning`、`error` 和 `alert` 函数可用于显示信息性消息：

```php
use function Laravel\Prompts\info;

info('Package installed successfully.');
```



## 表格

`table` 函数可以轻松显示多行多列的数据。你只需要提供表头和表格数据即可：

```php
use function Laravel\Prompts\table;

table(
    headers: ['Name', 'Email'],
    rows: User::all(['name', 'email'])->toArray()
);
```

## 旋转指示器

`spin` 函数会在执行指定回调时显示一个加载中的旋转器，并可附带一条消息。它用于表示正在进行的操作，并在完成后返回回调的结果：

```php
use function Laravel\Prompts\spin;

$response = spin(
    message: 'Fetching response...',
    callback: fn () => Http::get('http://example.com')
);
```

> [!警告]
> `spin` 函数需要 `pcntl` PHP 扩展来实现旋转动画。如果该扩展不可用，则会显示静态版本的旋转器。

## 进度条

对于耗时较长的任务，显示一个进度条可以帮助用户了解任务完成的进度。使用 `progress` 函数，Laravel 会显示一个进度条，并在每次迭代给定的可迭代值时推进进度：

```php
use function Laravel\Prompts\progress;

$users = progress(
    label: 'Updating users',
    steps: User::all(),
    callback: fn ($user) => $this->performTask($user)
);
```

`progress` 函数的作用类似于 `map` 函数，它会返回一个数组，包含每次回调执行的返回值。

回调函数还可以接收 `Laravel\Prompts\Progress` 实例，从而允许你在每次迭代中修改标签和提示信息：

```php
$users = progress(
    label: 'Updating users',
    steps: User::all(),
    callback: function ($user, $progress) {
        $progress
            ->label("Updating {$user->name}")
            ->hint("Created on {$user->created_at}");

        return $this->performTask($user);
    },
    hint: 'This may take some time.'
);
```



有时，你可能需要对进度条的推进进行更手动的控制。首先，定义该过程将迭代的总步数。然后，在处理完每个项目后，通过 `advance` 方法推进进度条：

```php
$progress = progress(label: 'Updating users', steps: 10);

$users = User::all();

$progress->start();

foreach ($users as $user) {
    $this->performTask($user);

    $progress->advance();
}

$progress->finish();
```

## 清除终端

`clear` 函数可用于清除用户的终端：

```php
use function Laravel\Prompts\clear;

clear();
```

## 终端注意事项

#### 终端宽度

如果任何标签、选项或验证消息的长度超过用户终端的“列数”，它将会被自动截断以适配。请尽量缩短这些字符串的长度，以便在较窄的终端中也能正常显示。通常来说，74 个字符是一个相对安全的最大长度，可以兼容 80 字符宽度的终端。

#### 终端高度

对于任何接受 `scroll` 参数的提示，其配置值会自动缩减，以适配用户终端的高度（包括预留用于验证消息的空间）。

## 不支持的环境与回退方案

Laravel Prompts 支持 macOS、Linux 和带 WSL 的 Windows。由于 PHP Windows 版本的限制，目前无法在非 WSL 的 Windows 环境下使用 Laravel Prompts。

因此，Laravel Prompts 支持回退到其他实现，例如 [Symfony Console Question Helper](https://symfony.com/doc/current/components/console/helpers/questionhelper.html)。

> [!注意]
> 当在 Laravel 框架中使用 Laravel Prompts 时，每个提示的回退方案已经为你配置好，并会在不支持的环境中自动启用。



#### 回退条件

如果你没有使用 Laravel，或者需要自定义何时启用回退行为，你可以向 `Prompt` 类的 `fallbackWhen` 静态方法传递一个布尔值：

```php
use Laravel\Prompts\Prompt;

Prompt::fallbackWhen(
    ! $input->isInteractive() || windows_os() || app()->runningUnitTests()
);
```

#### 回退行为

如果你没有使用 Laravel，或者需要自定义回退行为，你可以向每个提示类的 `fallbackUsing` 静态方法传递一个闭包：

```php
use Laravel\Prompts\TextPrompt;
use Symfony\Component\Console\Question\Question;
use Symfony\Component\Console\Style\SymfonyStyle;

TextPrompt::fallbackUsing(function (TextPrompt $prompt) use ($input, $output) {
    $question = (new Question($prompt->label, $prompt->default ?: null))
        ->setValidator(function ($answer) use ($prompt) {
            if ($prompt->required && $answer === null) {
                throw new \RuntimeException(
                    is_string($prompt->required) ? $prompt->required : 'Required.'
                );
            }

            if ($prompt->validate) {
                $error = ($prompt->validate)($answer ?? '');

                if ($error) {
                    throw new \RuntimeException($error);
                }
            }

            return $answer;
        });

    return (new SymfonyStyle($input, $output))
        ->askQuestion($question);
});
```

必须为每个提示类单独配置回退。闭包会接收提示类的一个实例，并且必须返回与该提示匹配的合适类型。
