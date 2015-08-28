---

layout: default

---

# Яндекс

## **{{ site.presentation.title }}** {#cover}

<div class="s">
</div>

{% if site.presentation.nda %}
<div class="nda"></div>
{% endif %}

<div class="info">
	<p class="author">{{ site.author.name }}, <br/> {{ site.author.position }}</p>
</div>

## О чем доклад
* Два слова о парсерах
* Где применить
  * Конфиги
  * Языки разметки
  * Языки шаблонов
  * Язык программирования
  * Языки зарпосов
* О чем не буду рассказывать

## Примеры языков запросов
* SQL
* Cypher (Neo4j)
* XPath
* Язык запросов к Яндексу

## Задача
* Есть пользователь
* Есть монга
* Нет доверия
* Нет любви

## Синтаксис

{% highlight sql %}
author=zubchick AND title~=test AND created>=today()
{% endhighlight %}

{% highlight sql %}
(author=me() OR author=test_user) AND created="19-08-2015" AND type=bug
{% endhighlight %}


## Шаги
* Лексический анализ
* Парсинг
    * Промежуточное дерево разбора
    * Абстрактное синтаксическое дерево
* Компиляция


## Пишем свой парсер
{:.section}

### Лексический анализ


## Составные части

### Логические операторы
<pre><code class="language-sql" data-lang="sql">author=zubchick <span class="k">AND</span> title~=test <span class="k">AND</span> created>=today()
</code></pre>

* <code>AND</code>
* <code>OR</code>

## Составные части

### Операторы сравнения
<pre><code class="language-sql" data-lang="sql">author<span class="o">=</span>zubchick AND title<span class="o">~=</span>test AND created<span class="o">>=</span>today()
</code></pre>
* <code>~=</code>
* <code>&gt;=</code>
* <code>&lt;=</code>
* <code>=</code>
* <code>*=</code>
* etc.

## Составные части

### Имена полей
<pre><code class="language-sql" data-lang="sql"><span
class="ss">author</span>=zubchick AND <span class="ss">title</span>~=test AND <span class="ss">created</span>>=today()
</code></pre>

## Составные части

### Текст в кавычках и без
<pre><code class="language-sql" data-lang="sql">author=<span
class="ss">zubchick</span> AND title~=<span class="ss">test</span> AND created>=today()
</code></pre>


<pre><code class="language-sql" data-lang="sql">(author=me() OR author=<span
class="ss">test_user</span>) AND created=<span class="ss">"19-08-2015"</span> AND type=<span class="ss">bug</span>
</code></pre>


## Составные части

### Функции
<pre><code class="language-sql" data-lang="sql">author=zubchick AND title~=test AND created>=<span class="ss">today()</span>
</code></pre>

<pre><code class="language-sql" data-lang="sql">(author=<span class="ss">me()</span> OR author=test_user) AND created="19-08-2015" AND type=bug
</code></pre>


## Составные части

### Вспомогательные символы
* Скобочки <code>(</code> <code>)</code>
* Пробелы <code>&nbsp;</code> <code>\t</code> <code>\n</code>


## Лексер

{% highlight python %}
from funcparserlib.lexer import make_tokenizer, Token

SPECS = [
    ('CMP', (r'~=|>=|<=|@=|<|>|=',)),
    ('BR', (r'\(|\)',)),
    ('OP', (r'AND|OR',)),
    ('SPACE', (r'[ \t\r\n]+',)),
    ('STRING', (r'"(?:[^"\\]|\\.)*"',)),
    ('WORD', ('\w+',)),
]

tokenizer = make_tokenizer(SPECS)


def tokenize(query):
    return [tok for tok in tokenizer(query) if tok.type != 'SPACE']
{% endhighlight %}


## Токен

{% highlight python %}
class Token(object):
    def __init__(self, type, value, start=None, end=None):
        self.type = type
        self.value = value
        self.start = start
        self.end = end
{% endhighlight %}

## Проверяем
{% highlight python %}
In [3]: tokenize('author=zubchick AND title~=test AND created>=today()')
Out[3]:
[Token('WORD', 'author'),
 Token('CMP', '='),
 Token('WORD', 'zubchick'),
 Token('OP', 'AND'),
 Token('WORD', 'title'),
 Token('CMP', '~='),
 Token('WORD', 'test'),
 Token('OP', 'AND'),
 Token('WORD', 'created'),
 Token('CMP', '>='),
 Token('WORD', 'today'),
 Token('BR', '('),
 Token('BR', ')')]
{% endhighlight %}


## Пишем свой парсер
{:.section}

### Синтаксический анализ


## Грамматика

### Расширенная форма Бэкуса — Наура

{% highlight ebnf %}
expr       = orexpr;

orexpr     = andexpr, {"OR", andexpr};
andexpr    = basexpr, {"AND", basexpr};
basexpr    = "(" expr ")" | fieldexpr;

fieldexpr  = WORD, operator, (function | value);
operator   = "~=" | ">=" | "<=" | "<" | ">" | "=" | "@=";
function   = WORD, "(", ")";
value      = STRING | WORD;
{% endhighlight %}


## Синтаксис

{% highlight sql %}
author=zubchick AND title~=test AND created>=today()
{% endhighlight %}

{% highlight sql %}
(author=me() OR author=test_user) AND created="19-08-2015" AND type=bug
{% endhighlight %}


## Теперь тоже самое на python

{% highlight python %}
from funcparserlib.parser import some, a, many, skip, forward_decl

# operator: '~=' | '>=' | '<=' | '<' | '>' | '=' | '@='
operator = some(lambda tok: tok.type == 'CMP')

string = some(lambda tok: tok.type == 'STRING')
word = some(lambda tok: tok.type == 'WORD')

OR = a(Token('OP', 'OR'))
AND = a(Token('OP', 'AND'))
{% endhighlight %}

## Field expression

{% highlight python %}
open_brace = skip(a(Token('BR', '(')))
close_brace = skip(a(Token('BR', ')')))
function = word + open_brace + close_brace

value = string | word
fieldexpr = word + operator + (function | value)
{% endhighlight %}


## Expression

{% highlight python %}
expr = forward_decl()

basexpr = open_brace + expr + close_brace | fieldexpr
andexpr = basexpr + many(AND + basexpr)
orexpr = andexpr + many(OR + andexpr)
expr.define(orexpr)
{% endhighlight %}


## Проверяем

{% highlight python %}
In [8]: expr.parse(tokenize('author=zubchick AND title~=test AND created>=today()'))
Out[8]:
(Token('WORD', 'author'),
 Token('CMP', '='),
 Token('WORD', 'zubchick'),
 [(Token('OP', 'AND'),
   (Token('WORD', 'title'), Token('CMP', '~='), Token('WORD', 'test'))),
  (Token('OP', 'AND'),
   (Token('WORD', 'created'), Token('CMP', '>='), Token('WORD', 'today')))],
 [])
{% endhighlight %}


## Синтаксический анализ
{:.section}

### AST

## &nbsp;
{:.big-code}
{% highlight python %}
class AST:
    children = ()


class Operator(AST):
    value = None

    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return "%s %s (%s)" % (self.__class__.__name__,
                               self.value, map(repr, self.children))


class LogicalOperator(Operator):
    pass


class CmpOperator(Operator):
    pass
{% endhighlight %}

## &nbsp;
{:.big-code}
{% highlight python %}
class Function(AST):
    def __init__(self, text):
        self.name = text.text

    def __repr__(self):
        return "%s()" % (self.name)


class Text(AST):
    def __init__(self, tok):
        self.text = tok.value

    def __repr__(self):
        return "Text(%s)" % self.text
{% endhighlight %}


## &nbsp;
{:.big-code}
{% highlight python %}
class AndOp(LogicalOperator):
    value = 'AND'

class OrOp(LogicalOperator):
    value = 'OR'

class GtOp(CmpOperator):
    value = '>'

class LtOp(CmpOperator):
    value = '<'

class GteOp(CmpOperator):
    value = '<='

class LteOp(CmpOperator):
    value = '>='

class RegexpOp(CmpOperator):
    value = '~='

class ContainsOp(CmpOperator):
    value = '@='
{% endhighlight %}



## Добавляем колбеки
{% highlight python %}
operator = some(lambda tok: tok.type == 'CMP') >> choose_class

string = some(lambda tok: tok.type == 'STRING') >> Text
word = some(lambda tok: tok.type == 'WORD') >> Text

function = word + open_brace + close_brace >> Function

OR = a(Token('OP', 'OR')) >> lambda tok: OrOp
AND = a(Token('OP', 'AND')) >> lambda tok: AndOp
{% endhighlight %}


## Разворачиваем в дерево
{:.images .two}

<img width="400px" src="pictures/ast2.svg">
*Текст*

<img width="400px" src="pictures/ast1.svg">
*Текст*


## Разворачиваем в дерево
{% highlight python %}
def eval(data):
    lft, args = data
    return reduce(lambda arg1, (f, arg2): f([arg1, arg2]), args, lft)
{% endhighlight %}







<!-- Рыба -->


## Верхний колонтитул
{:.section}

### Название раздела

## Заголовок

### Вводный текст (первый уровень текста)

*  Второй уровень текста
	* Третий уровень текста (буллиты)

	1. Четвертый уровень текста

## Заголовок

### Вводный текст (первый уровень текста)
![placeholder](pictures/vertical-placeholder.png){:.right-image}

*  Второй уровень текста
	* Третий уровень текста (буллиты)
	* Третий уровень текста (буллиты)

	1. Четвертый уровень текста

## &nbsp;
{:.with-big-quote}
> Цитата

Текст
{:.note}

## Пример подсветки кода на JavaScript

~~~ javascript
!function() {
    var jar,
        rstoreNames = /[^\w]/g,
        storageInfo = window.storageInfo || window.webkitStorageInfo,
        toString = "".toString;

    jar = this.jar = function( name, storage ) {
        return new jar.fn.init( name, storage );
    };

    jar.storages = [];
    jar.instances = {};
    jar.prefixes = {
        storageInfo: storageInfo
    };

    jar.prototype = this.jar.fn = {
        constructor: jar,

        version: 0,

        storages: [],
        support: {},

        types: [ "xml", "html", "javascript", "js", "css", "text", "json" ],

        init: function( name, storage ) {

            // Name of a object store must contain only alphabetical symbols or low dash
            this.name = name ? name.replace( rstoreNames, "_" ) : "jar";
            this.deferreds = {};

            if ( !storage ) {
                this.order = jar.order;
            }

            // TODO – add support for aliases
            return this.setup( storage || this.storages );
        },

        // Setup for all storages
        setup: function( storages ) {
            this.storages = storages = storages.split ? storages.split(" ") : storages;

            var storage,
                self = this,
                def = this.register(),
                rejects = [],
                defs = [];

            this.stores = jar.instances[ this.name ] || {};

            // Jar store meta-info in lc, if we don't have it – reject call
            if ( !window.localStorage ) {
                window.setTimeout(function() {
                    def.reject();
                });
                return this;
            }

            // Initiate all storages that we can work with
            for ( var i = 0, l = storages.length; i < l; i++ ) {
                storage = storages[ i ];

                // This check needed if user explicitly specified storage that
                // he wants to work with, whereas browser don't implement it
                if ( jar.isUsed( storage ) ) {

                    // If jar with the same name was created, do not try to re-create store
                    if ( !this.stores[ storage ] ) {

                        // Initiate storage
                        defs.push( this[ storage ]( this.name, this ) );

                        // Initiate meta-data for this storage
                        this.log( storage );
                    }

                } else {
                    rejects.push( storage );
                }
            }

            if ( !this.order ) {
                this.order = {};

                for ( i = 0, l = this.types.length; i < l; i++ ) {
                    this.order[ this.types[ i ] ] = storages;
                }
            }

            if ( rejects.length == storages.length ) {
                window.setTimeout(function() {
                    def.reject();
                });

            } else {
                jar.when.apply( this, defs )
                    .done(function() {
                        jar.instances[ this.name ] = this.stores;

                        window.setTimeout(function() {
                            def.resolve([ self ]);
                        });
                    })
                    .fail(function() {
                        def.reject();
                    });
            }
            return this;
        }
    };

    jar.fn.init.prototype = jar.fn;

    jar.has = function( base, name ) {
        return !!jar.fn.meta( name, base.replace( rstoreNames, "_" ) );
    };
}.call( window );
~~~

## Пример подсветки кода
{:.code-with-text}

Вводный текст

~~~ javascript
var jar,
    rstoreNames = /[^\w]/g,
    storageInfo = window.storageInfo || window.webkitStorageInfo,
    toString = "".toString;

jar = this.jar = function( name, storage ) {
    return new jar.fn.init( name, storage );
};
~~~

## &nbsp;
{:.big-code}

~~~ javascript
!function() {
    var jar,
        rstoreNames = /[^\w]/g,
        storageInfo = window.storageInfo || window.webkitStorageInfo,
        toString = "".toString;

    jar = this.jar = function( name, storage ) {
        return new jar.fn.init( name, storage );
    };

    jar.storages = [];
    jar.instances = {};
    jar.prefixes = {
        storageInfo: storageInfo
    };
}.call( window );
~~~

## LaTeX

Библиотека для латекса довольно тяжелая, а нужна она в редких случаях.
Поэтому она не включена в репу, ее нужно либо установить через bower либо иметь интернет.

When $a \ne 0$, there are two solutions to \(ax^2 + bx + c = 0\) and they are
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}.$$

## Заголовок
{:.images}

![](pictures/horizontal-placeholder.png)
*Текст*

![](pictures/horizontal-placeholder.png)
*Текст*

![](pictures/horizontal-placeholder.png)
*Текст*

## Заголовок
{:.images .two}

![](pictures/horizontal-middle-placeholder.png)
*Текст*

![](pictures/horizontal-middle-placeholder.png)
*Текст*

## Заголовок
{:.center}

![](pictures/horizontal-big-placeholder.png){:.tmp}

## **![](pictures/cover-placeholder.png)**

## ![](pictures/horizontal-cover-placeholder.png)
{:.cover}

## Таблица

|  Locavore      | Umami       | Helvetica | Vegan     |
+----------------|-------------|-----------|-----------+
| Fingerstache   | Kale        | Chips     | Keytar    |
| Sriracha       | Gluten-free | Ennui     | Keffiyeh  |
| Thundercats    | Jean        | Shorts    | Biodiesel |
| Terry          | Richardson  | Swag      | Blog      |
+----------------|-------------|-----------|-----------+


## Таблица с дополнительным полем

{:.with-additional-line}
|  Locavore      | Umami       | Helvetica | Vegan     |
+----------------|-------------|-----------|-----------+
| Fingerstache   | Kale        | Chips     | Keytar    |
| Sriracha       | Gluten-free | Ennui     | Keffiyeh  |
| Thundercats    | Jean        | Shorts    | Biodiesel |
| Terry          | Richardson  | Swag      | Blog      |
+----------------|-------------|-----------|-----------+
| Terry          | Richardson  | Swag      | Blog      |

## **Контакты** {#contacts}

<div class="info">
<p class="author">{{ site.author.name }}</p>
<p class="position">{{ site.author.position }}</p>

    <div class="contacts">
        <p class="contacts-left mail">zubchick@yandex-team.ru</p>
        <p class="contacts-left contacts-top twitter">@zubchick</p>

    </div>
</div>
