from gettext import gettext as _
SKILL_NAME = "パパの目安箱"

LAUNCH_NOT_PERSONALIZE = _(
    "すみません。誰の声か識別できませんでした。このスキルでは音声プロフィールの登録が必要です。" \
    + "もし音声プロフィールの登録がまだの場合はアレクサアプリにで音声プロフィールを登録してください。" \
    + "すでに有効にされている場合は、聞き取れなかった可能性がありますので再度お試しください。" \
    + "スキルの詳細を知りたい場合は、「アレクサ、{}を開いて、ヘルプ」といってください".format(SKILL_NAME))
LAUNCH_NOT_CLASS = _(
    "{} はパパ以外の家族がパパへのメッセージを登録し、パパがそのメッセージを聞くスキルです。".format(SKILL_NAME) \
    + "まずはあなたがパパなのか違うのかを教えてください。「パパです」、もしくは、「違う人です」と答えてください" )
LAUNCH_IS_PARENT = _(
    "こんにちは、<alexa:name type='first' personId='{}'/>さん。「伝言を確認」というとメッセージを聞けます。" \
    + "使い方を知りたい場合は「ヘルプ」といってください。")
LAUNCH_IS_CHILD = _(
    "こんにちは、<alexa:name type='first' personId='{}'/>さん。「伝言をする」というとメッセージを登録できます。" \
    + "登録したメッセージを聞くには「伝言を確認」と言ってくださいね。" \
    + "")
ANSWER_CLASS_NOT_PERSONALIZE = _(
    "すみません。誰の声か識別できませんでした。このスキルでは音声プロフィールの登録が必要です。" \
    + "「パパです」、もしくは「違う人です」ともう一度、ゆっくりと言ってみてください。" )
ANSWER_CLASS_IS_PARENT = _(
    "承知しました、<alexa:name type='first' personId='{}'/>さん。それでは「パパ」として登録しますね。" \
    "<alexa:name type='first' personId='{}'/>さんは、みんなの「メッセージ」を確認する事ができます。" \
    + "メッセージの登録がまだの場合は、他の人の音声プロフィールを登録したあと、{}で遊んでもらってください。".format(SKILL_NAME) \
    + "メッセージが登録されるとそれを聞く事ができますよ。使い方を知りたい場合は「ヘルプ」と言ってください。")
ANSWER_CLASS_IS_CHILD = _(
    "承知しました。パパではないのですね。<alexa:name type='first' personId='{}'/>さんは、「メッセージ」を登録する事ができます。" \
    "「伝言をする」と言ってみてください。")
PREMIUM_INFO_MSG = _(
    "こんにちは")
BUY_MSG = _(
    "こんにちは")
BUY_COMPLETE_MSG = _(
    "こんにちは")
BUY_CANCEL_MSG = _(
    "こんにちは")
CANCEL_SUBSCRIPTION_MSG = _(
    "こんにちは")
WELCOME_MESSAGE = _(
    "こんにちは")
WISH_ADD_MSG = _("{}、ですね。メッセージを登録しました。登録したメッセージを確認するときは「伝言を確認」と言ってくださいね。")
WISH_ADD_PARENT_MSG = _("{}、ですね。おや？自分への伝言ですか？登録したメッセージを確認するときは「伝言を確認」と言ってくださいね。")
WISH_ADD_ERR_MSG = _("すみません。メッセージが確認できませんでした。もう一度最初からお願いします。")
WISH_ADD_NOT_PERSONALIZE = _(
    "すみません。誰の声か識別できませんでした。このスキルでは音声プロフィールの登録が必要です。" \
    + "もう一度、「伝言をする」とゆっくりと言ってみてください。" )
WISH_LIST_NOT_PERSONALIZE = _(
    "すみません。誰の声か識別できませんでした。このスキルでは音声プロフィールの登録が必要です。" \
    + "もう一度、「伝言を確認」とゆっくりと言ってみてください。" )
WISH_LIST_CHILD_MSG = _(
    "登録されてるメッセージは<break time='500ms' />{}<break time='500ms' />です。" \
    + "メッセージを消したい場合には「登録を削除」と言ってくださいね。")
WISH_LIST_PARENT_MSG = _(
    "<alexa:name type='first' personId='{}'/><break time='300ms' />さんの登録されてるメッセージは" \
    + "<break time='500ms' />{}<break time='500ms' />です。" )
WISH_LIST_NONE_CHILD_MSG = _("まだメッセージが登録されていないようです。登録する場合には「伝言をする」と言ってみてね。")
WISH_LIST_NONE_PARENT_MSG = _("まだメッセージが登録されていないようです。メッセージが登録されるのを待ちましょう。")
WISH_DELETE_NOT_PERSONALIZE = _(
    "すみません。誰の声か識別できませんでした。このスキルでは音声プロフィールの登録が必要です。削除したい場合には、" \
    + "もう一度、「伝言を削除」からやりなおしてみてください。" )
WISH_DELETE_YES_MSG = _(
    "メッセージを削除しました。新しくメッセージを登録するには「伝言をする」と言ってください。")
WISH_DELETE_NO_MSG = _(
    "メッセージの削除を取りやめました。新しくメッセージを登録するには「伝言をする」と言ってください。")
WISH_DELETE_NON_MSG = _(
    "メッセージが登録されていません。新しくメッセージを登録するには「伝言をする」と言ってください。")
ANSWER_CLASS_LIMIT_MSG = _(
    "すみません。現在、パパひとりとパパ以外の家族をふたりまでの利用しかできません。次は何をしますか？"
)
HELP_MSG = _(
    "{} は家族がパパにメッセージを登録し、パパがそのメッセージを聞くスキルです。".format(SKILL_NAME) \
    + "使用するにはアレクサアプリで音声プロフィールの登録が必要です。" \
    + "メッセージの登録は、「伝言を聞いて」。" \
    + "メッセージの確認は、「伝言を確認」。" \
    + "メッセージを消す時は、「伝言を削除」。" \
    + "プレミアム機能について知りたい方は、「プレミアム機能について教えて」。" \
    + "のように遊んでください。何をしますか？" )
PREMIUM_INFO_MSG = _("パパの目安箱スキルはパパがひとりとその他の家族がふたりまで利用できるスキルです。" \
    + "プレミアム機能を購入する事によってその制限がなくなり、" \
    + "音声プロファイルを登録した方であれが何人でも利用ができるようになります。購入する場合には「プレミアム機能を購入」といってください")
SHOPPING_T_MSG = _(
    "すでにプレミアム機能が有効になっています。キャンセルする場合には「プレミアム機能をキャンセル」といってください")
SHOPPING_F_MSG = _(
    "プレミアム機能の購入はされていません。購入する場合には「プレミアム機能を購入」といってください")
GOODBYE_MSG = _("使ってくれてありがとう。ではまた")
REFLECTOR_MSG = _("You just triggered {}")
ERROR = _("すみません。よく聞き取れませんでした。もう一度お願いします。")
