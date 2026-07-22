# SampleWiki

ChatGPTからGitHub Wikiを読み書きするための検証用Wikiです。

## 目的

- GitHub Wikiを外部AIから編集する
- MarkdownページをGitで管理する
- WikiベースSNSの概念を試作する
- ページ間リンクと更新履歴を検証する

## ページ

- [[WikiベースSNS]]
- [[運用ルール]]
- [[ChatGPT連携]]

## 編集方式

このWikiの原本は通常リポジトリ内の `docs/wiki` ディレクトリです。

`main` ブランチへ変更がpushされると、GitHub ActionsがWikiリポジトリへ同期します。
