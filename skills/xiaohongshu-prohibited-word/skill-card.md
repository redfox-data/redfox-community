## Description: <br>
基于站长之家官方违禁词库，专攻小红书平台审核规则，支持文案、文件（TXT/DOC/DOCX）、图片、链接多形式输入，快速输出违禁词标记和上下文智能替换建议。 <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[if530770](https://clawhub.ai/user/if530770) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External creators, brand and e-commerce operators, marketing teams, and content reviewers use this skill to check Xiaohongshu copy, uploaded text documents, images with extracted text, or webpage text for prohibited terms before publishing. It returns flagged terms, replacement suggestions, and an optimized Markdown draft. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Checked copy, extracted file text, or fetched webpage text is sent to an external detection service. <br>
Mitigation: Use only with content that may be shared with that service, or configure a controlled endpoint with XHS_SENSITIVE_WORD_API_URL before handling confidential material. <br>
Risk: Prohibited-word results and replacement suggestions are advisory and may not fully reflect current Xiaohongshu policy or a publisher's compliance obligations. <br>
Mitigation: Review flagged terms and suggested replacements against the actual product claims, operating scope, and publication policy before posting. <br>


## Reference(s): <br>
- [Core workflow](references/core_workflow.md) <br>
- [ClawHub skill page](https://clawhub.ai/if530770/xhs-prohibited-word) <br>


## Skill Output: <br>
**Output Type(s):** [Markdown, Guidance, Shell commands] <br>
**Output Format:** [Markdown with tables, inline emphasis, and script command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Does not generate files; long inputs are gated at 3000 and 10000 characters; supports extracted text from TXT, DOC, DOCX, images, and webpages.] <br>

## Skill Version(s): <br>
1.0.5 (source: server release metadata; artifact frontmatter states 1.0.4) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
