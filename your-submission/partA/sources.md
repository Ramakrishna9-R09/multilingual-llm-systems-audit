# Part A sources and assets

- Meta AI, [FLORES-200 documentation](https://github.com/facebookresearch/flores/blob/main/flores200/README.md). The corpus description, language codes, split description, and official archive link are sourced here. The included FLORES-derived text is licensed [CC-BY-SA 4.0](https://github.com/facebookresearch/flores/blob/main/LICENSE_CC-BY-SA).
- Meta AI, [FLORES-200 official archive](https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz). `prepare_flores.py` records its SHA-256 in the generated manifest.
- Facebook AI, [XLM-RoBERTa base model card](https://huggingface.co/FacebookAI/xlm-roberta-base). The XLM-R tokenizer asset used here is its public SentencePiece model.
- OpenAI, [tiktoken repository](https://github.com/openai/tiktoken). The `gpt2` encoding is loaded with `tiktoken.get_encoding("gpt2")`.

The experiment does not use a hosted inference API, a paid corpus, or model
outputs to manufacture evaluation text.
