from transformers import BartTokenizer, BartForConditionalGeneration
import torch


class CrispySummarizer:
    """
    CrispySummarizer is a wrapper class for the BartForConditionalGeneration model
    from the transformers library. It is used to generate summaries from articles
    """

    device = "cpu"
    model = BartForConditionalGeneration.from_pretrained("Yale-LILY/brio-cnndm-uncased")
    model.to(device)
    model.eval()

    tokenizer = BartTokenizer.from_pretrained("Yale-LILY/brio-cnndm-uncased")
    max_length = 1024

    def __call__(self, article, max_length=120, min_length=40) -> str:
        # article = article.lower()
        inputs = self.tokenizer(
            article,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
            truncation=True,
        ).to(self.device)
        summary_ids = self.model.generate(
            inputs["input_ids"], max_length=max_length, min_length=min_length
        )
        return self.tokenizer.batch_decode(
            summary_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
