---
layout: redirect
redirect: https://lukeonpython.blog/2020/06/process-manager-vs-ddd-aggregate/
title: Process manager VS DDD Aggregate
categories: [ddd]
tags: [ddd, component, code architecture]
---
DDD Aggregate is responsible for encapsulating business logic for the component. But we need to be aware that when we are implementing business logic for a long time process that is coordinating many components, like subscription trial, we have another building block for this. It's a process manager. Below I pointed out some differences between these two building blocks.
