"""Gradio WebUI 主应用。

提供文档生成的图形界面。
"""

import gradio as gr
from typing import Optional


def create_interface() -> gr.Blocks:
    """创建 Gradio 界面。

    Returns:
        Gradio Blocks 界面
    """
    with gr.Blocks(
        title="DocuGen",
        theme=gr.themes.Soft(),
    ) as interface:
        gr.Markdown(
            """
            # DocuGen - 多智能体文档生成系统

            使用自然语言需求生成专业文档，支持模板和知识库增强。
            """
        )

        with gr.Tabs():
            # 文档生成标签
            with gr.TabItem("文档生成"):
                with gr.Row():
                    with gr.Column(scale=2):
                        requirements = gr.Textbox(
                            label="文档需求",
                            placeholder="描述您想要生成的文档...\n\n"
                            "例如：为一个新的 AI 客户服务聊天机器人创建项目提案，"
                            "包括执行摘要、问题陈述、建议方案、时间表和预算估算。",
                            lines=10,
                        )

                        with gr.Row():
                            template_dropdown = gr.Dropdown(
                                label="文档模板",
                                choices=[],
                                value=None,
                                interactive=True,
                            )
                            refresh_templates_btn = gr.Button("刷新模板", size="sm")

                        with gr.Row():
                            max_revisions = gr.Slider(
                                label="最大修订次数",
                                minimum=1,
                                maximum=5,
                                value=3,
                                step=1,
                            )
                            generate_btn = gr.Button(
                                "生成文档",
                                variant="primary",
                                size="lg",
                            )

                    with gr.Column(scale=1):
                        task_id_display = gr.Textbox(
                            label="任务 ID",
                            interactive=False,
                        )
                        status_display = gr.Textbox(
                            label="状态",
                            interactive=False,
                        )
                        check_status_btn = gr.Button("检查状态")

                with gr.Accordion("生成的文档", open=True):
                    generated_doc = gr.Markdown(
                        label="生成结果",
                        value="等待生成...",
                    )

                    with gr.Row():
                        copy_btn = gr.Button("复制文档")
                        download_btn = gr.Button("下载文档")

            # 模板管理标签
            with gr.TabItem("模板管理"):
                with gr.Row():
                    with gr.Column():
                        template_name = gr.Textbox(
                            label="模板名称",
                            placeholder="例如：项目提案模板",
                        )
                        template_desc = gr.Textbox(
                            label="模板描述",
                            placeholder="描述模板的用途...",
                            lines=2,
                        )
                        template_sections = gr.Code(
                            label="章节定义 (JSON)",
                            language="json",
                            value='[\n  {"name": "执行摘要", "required": true},\n  {"name": "主体内容", "required": true}\n]',
                        )
                        create_template_btn = gr.Button("创建模板")

                    with gr.Column():
                        template_list = gr.Dataframe(
                            headers=["ID", "名称", "描述", "创建时间"],
                            label="现有模板",
                        )
                        refresh_list_btn = gr.Button("刷新列表")
                        delete_template_id = gr.Textbox(
                            label="要删除的模板 ID",
                        )
                        delete_template_btn = gr.Button("删除模板")

            # 知识库标签
            with gr.TabItem("知识库"):
                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="上传文档",
                            file_types=[".pdf", ".docx", ".txt", ".md"],
                        )
                        doc_title = gr.Textbox(
                            label="文档标题（可选）",
                        )
                        upload_btn = gr.Button("上传")

                    with gr.Column():
                        knowledge_list = gr.Dataframe(
                            headers=["ID", "标题", "类型", "上传时间"],
                            label="知识库文档",
                        )
                        refresh_knowledge_btn = gr.Button("刷新列表")
                        delete_knowledge_id = gr.Textbox(
                            label="要删除的文档 ID",
                        )
                        delete_knowledge_btn = gr.Button("删除文档")

            # 任务监控标签
            with gr.TabItem("任务监控"):
                task_filter = gr.Dropdown(
                    label="状态过滤",
                    choices=["全部", "pending", "processing", "completed", "failed"],
                    value="全部",
                )
                refresh_tasks_btn = gr.Button("刷新任务列表")
                tasks_list = gr.Dataframe(
                    headers=["ID", "状态", "阶段", "修订次数", "创建时间"],
                    label="任务列表",
                )
                task_detail_id = gr.Textbox(
                    label="任务 ID（查看详情）",
                )
                view_task_btn = gr.Button("查看详情")
                task_detail = gr.JSON(label="任务详情")

        # 事件处理
        async def on_generate(requirements, template_id, max_revs):
            """处理生成请求。"""
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:7860/api/documents/generate",
                    json={
                        "requirements": requirements,
                        "template_id": template_id,
                        "knowledge_ids": [],
                        "max_revisions": max_revs,
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                data = response.json()
                return data["task_id"], "pending", "任务已创建，请点击检查状态"
            else:
                return "", "error", f"创建失败: {response.text}"

        async def on_check_status(task_id):
            """检查任务状态。"""
            if not task_id:
                return "pending", "请先生成文档", "等待生成..."

            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:7860/api/tasks/{task_id}",
                    timeout=10.0,
                )

            if response.status_code == 200:
                data = response.json()
                doc = data.get("generated_document") or "仍在生成中..."
                return data["status"], data.get("error") or f"阶段: {data['current_stage']}", doc
            else:
                return "error", "获取状态失败", ""

        generate_btn.click(
            on_generate,
            inputs=[requirements, template_dropdown, max_revisions],
            outputs=[task_id_display, status_display, generated_doc],
        )

        check_status_btn.click(
            on_check_status,
            inputs=[task_id_display],
            outputs=[status_display, generated_doc, generated_doc],
        )

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
