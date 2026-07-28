# Problem Statement

## Catering Knowledge Assistant

A home-kitchen meal delivery business in Klang Valley runs almost entirely out of one WhatsApp thread. The owner cooks, packs, delivers, and personally answers every question that arrives, roughly forty a week and mostly the same forty. The answers are correct only because they live in the owner's head, because the rules behind them are scattered across four places that never agree in one document: menu images redesigned every month, a subscription arrangement that was explained verbally, a refund practice that has never been written down, and holiday closures announced ad hoc when they happen. When the part-time helper takes the phone, they know the food but not the terms, so they either guess or wait for the owner to reply between batches. A wrong answer about delivery coverage or a refund costs a customer; a slow answer costs an order.

The harder half of the problem is that half the questions are not document questions at all. "How many meals do I have left" and "when does my cycle end" cannot be answered by reading any policy, because every subscriber starts on a different date and every public holiday pushes their cycle out by another service day. Across twenty subscribers that produces fourteen different end dates, and today the only way to answer is to count by hand through a notebook. So the business needs two different machines behind one conversation: grounded retrieval over the written rules, where the binding policy must win over the convenient summary and a holiday notice must override the standing schedule, and governed queries over the actual records, where the model may choose which question to ask of the database but never how to ask it.

---

**Persona:** owner-operator of a weekday meal delivery business in Shah Alam and Kota Kemuning, about 35 meals a day across lunch and dinner, RM 13,000 to RM 16,000 a month, one owner plus two or three helpers, run from WhatsApp on a phone. Secondary user: the part-time helper who answers messages but does not know the terms.

**Build type:** C, Career Path Builder. Advances RAG Systems (weight 10 FDE, from 1-2 to 3) and Vector Databases (from 0-1 to 3), plus Evaluation.

**Moat cleared:** governed access to structured data, deterministic authority precedence, and computed retrieval rigor. NotebookLM would answer the document half faster; it cannot query the records, cannot enforce that an override document outranks a standing policy, and gives no way to measure how often retrieval is wrong.
