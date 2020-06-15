---
layout: post
title: Process manager VS DDD Aggregate
categories: [ddd]
tags: [ddd, component, code architecture]
---
DDD Aggregate is responsible for encapsulating business logic for the component. But we need to be aware that when we are implementing business logic for a long time process that is coordinating many components, like subscription trial, we have another building block for this. It's a process manager. Below I pointed out some differences between these two building blocks.

# DDD Aggregate
 - autonomous/independent
 - no long time processes
 - all data encapsulated inside
 - reacts on commands
 - emits events

# Process Manager
 - depends on other components
 - coordinates long time process
 - is aware of the actual process state
 - compensates issues in the process
 - reacts on events
 - emits commands

# Stock Example
I will give you an example of a component that has both: process manager and DDD aggregate.
Let's imagine a situation that we are synchronizing stock of products listed on many marketplaces (eBay US, eBay UK, Amazon, etc.). So whenever there is a sale we need to propagate this info to all listing to prevent overselling. So there is DDD aggregate which responsibility is to calculate stock quantity for every listing. With some business logic stock distribution. And we have a process manager which takes care of distributing proper quantities to every marketplace and reacts to situations when there are issues with this propagation.

## DDD Aggregate responsibility:
 - decide on a distribution of product stock quantities on marketplaces/sites
 - have business logic about marketplaces and what to do on low-level stocks (which marketplace have stock and which is not so important from business level)
 - have a business context about quantity distribution
 
## Stock sync process manages:
 - know stock distribution status
 - understands the process of stock synchronization between marketplaces
 - know how to compensate issues on stock sync
 - manages stock synchronization in time, until quantity distribution is coherent
 