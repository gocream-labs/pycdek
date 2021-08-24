# PyCDEK 2

Python library for CDEK API v2.0

API - [ru][api_url_ru] [en][api_url_en]



## Develop

При разработке используем [git flow][git_flow_atlassian]

config для git flow:

```
[gitflow "branch"]
    master = master
    develop = dev
[gitflow "prefix"]
    feature = feature/
    bugfix = bugfix/
    release = release/
    hotfix = hotfix/
    support = support/
    versiontag =
```



## Release & Versioning

Версии обновляем в соответствии с [мануалом][semver] в это же время репо ведём в соответствии с [gitflow][git_flow].

Общий алгоритм дейтсвий следующий:

0. Write your brilliant code;

1. Start `git flow release start X.X.X[-x.X]`;

2. Обновляем версию в *\_\_init\_\_.py* до соответствующей версии;

3. Коммитим все изменения;

4. Релизим `git flow release finish X.X.X`.

> Незабываем использовать *rc* (release candidate) версии для тестирования обновлений, перед релизом новой стабильной версии.



## TO DO:

* tests
* unittests
* test flask app


[api_url_ru]:https://confluence.cdek.ru/pages/viewpage.action?pageId=29923741
[api_url_en]:https://confluence.cdek.ru/pages/viewpage.action?pageId=33828739
[semver]: https://semver.org/lang/ru/
[git_flow]: https://jeffkreeftmeijer.com/git-flow/
[git_flow_atlassian]: https://www.atlassian.com/ru/git/tutorials/comparing-workflows/gitflow-workflow
