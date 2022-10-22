---
title: "Cross Entropy and KL Divergence"
date: 2022-10-22T20:02:01+07:00
draft: true
author: "Quan Dang"
type: "technical_note"
desciptions: ""
---


In information theory, entropy reveals the **uncertainty** in transmit information

[Entropy in compression](https://www.youtube.com/watch?v=M5c_RFKVkko&t=597s)
- Weather in some where,

|             | Sunny | Cloudy | Foggy | Rainy |
| ----------- | ----- | ------ | ----- | ----- |
| Probability (true distribution) | 1/4   | 1/4    | 1/4   | 1/4   |
| Encoded     (predicted distribution)| 00    | 01     | 10    | 11    |

&#8594; $2^2$, need `2` bit when 4 states have equally probability

- Weather in a desert

$P(sunny) = 1$, how many bit do we need to transfer this information? &#8594; `0` bit

- Low entropy versus high entropy

  - Low entropy: easy to guess.

  - High entropy: for example, when you toss a fair coin (50/50)

- Construction formula

$$- \sum p\cdot log{p} = \dfrac{1}{4}\times 2 + \dfrac{1}{4}\times 2 + \dfrac{1}{4}\times 2 + \dfrac{1}{4}\times 2 = 2$$ (the average message length)

- Weather in some where,

|             | Sunny | Cloudy | Foggy | Rainy |
| ----------- | ----- | ------ | ----- | ----- |
| Probability (true distribution)| 1/2   | 1/4    | 1/8   | 1/8   |
| Encoded     (predicted distribution)| 0     | 01     | 110   | 111   |

$$-\sum p\cdot log{p} = \dfrac{1}{2}\times 1 + \dfrac{1}{4}\times 2 + \dfrac{1}{8}\times 3 + \dfrac{1}{8}\times 3 = 7/4$$ (the average message length)

[Cross entropy - KL divergence](https://www.youtube.com/watch?v=ErfnhcEV1O8&t=502s)

#### Cross entropy formula:

$$H(p, q) = - \sum_i p_i \cdot log q_i$$

when the prediction is perfect, the cross entropy is equal to the entropy.
The cross-entropy is always equal or greater than the entropy

#### KL-divergence

$$D_{KL}(p\parallel q) = H(p, q) - H(p)$$ 
KL-divergence is equal to the cross-entropy minus the entropy


### Additional resouce
- [Things that confused me about cross-entropy](https://chris-said.io/2020/12/26/two-things-that-confused-me-about-cross-entropy/)