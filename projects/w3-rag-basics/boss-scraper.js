/**
 * BOSS直聘搜索结果导出脚本
 *
 * 用法：
 * 1. BOSS 搜索结果页，往下划加载足够多岗位
 * 2. F12 → Console → 粘贴整段代码 → 回车
 * 3. CSV 自动下载
 * 4. 继续往下划 → 再跑一次 → 只导出新的，不重复
 *
 * 去重规则：
 * - 同一公司+同一岗位（多个HR发布），只保留第一个
 * - 同一链接的岗位只导出一次（跨次运行也去重）
 *
 * 重置：localStorage.removeItem('boss_exported_jobs')
 */

(function () {
  // --- 归一化：去掉括号、空格、标点，用于比较 ---
  function normalize(s) {
    return (s || '')
      .replace(/[（(].*?[)）]/g, '')   // 去掉括号及内容
      .replace(/[\s\-_·•]/g, '')       // 去掉空格横线下划线
      .toLowerCase();
  }

  // --- 提取岗位数据 ---
  function extractJob(card) {
    const getText = (sel) => {
      const el = card.querySelector(sel);
      return el ? el.textContent.trim() : '';
    };

    const nameEl =
      card.querySelector('a[ka^="search_list_"]') ||
      card.querySelector('.job-name a, .job-title a, [class*="job-name"] a, [class*="job-title"] a');
    const linkEl = nameEl || card.querySelector('a[href*="/job_detail/"]');
    const companyEl =
      card.querySelector('.company-name a, .company-text a, [class*="company-name"] a, [class*="company"] a');

    const link = linkEl ? linkEl.href : '';
    const jobId = link.match(/job_detail\/([a-zA-Z0-9]+)\.html/)?.[1] || link;

    const tags = Array.from(
      card.querySelectorAll('.tag-list li, .job-tag, [class*="tag"] span, .experience, .degree')
    )
      .map((t) => t.textContent.trim())
      .filter(Boolean);

    const jobName = nameEl ? nameEl.textContent.trim() : getText('.job-name, .job-title, [class*="job-name"], [class*="job-title"]');
    const companyName = companyEl ? companyEl.textContent.trim() : getText('.company-name, [class*="company-name"]');

    return {
      id: jobId,
      name: jobName,
      salary: getText('.salary, [class*="salary"], [class*="red"]'),
      company: companyName,
      location: tags.find((t) => t.includes('区') || t.includes('街道')) || '',
      tags: tags.join(' / '),
      link: link,
      // 去重用：归一化的公司+岗位名
      dedupKey: normalize(companyName) + '|||' + normalize(jobName),
    };
  }

  // --- 读取历史记录 ---
  const exported = new Set(JSON.parse(localStorage.getItem('boss_exported_jobs') || '[]'));
  const exportedKeys = new Set(JSON.parse(localStorage.getItem('boss_exported_keys') || '[]'));

  // --- 抓取当前页面 ---
  const cards = document.querySelectorAll('li.job-card-box, div.job-card-body, [class*="job-card"]');
  const jobs = [];
  const seenLink = new Set();
  const seenKey = new Set();

  cards.forEach((card) => {
    const job = extractJob(card);

    // 跳过没拿到链接的
    if (!job.link) return;

    // 去重：同一次运行中，相同链接不重复
    if (seenLink.has(job.link)) return;
    seenLink.add(job.link);

    // 去重：同一公司+同一岗位（多HR发布）
    if (seenKey.has(job.dedupKey)) return;
    seenKey.add(job.dedupKey);

    // 去重：之前运行已导出过的链接或公司+岗位
    if (exported.has(job.id) || exportedKeys.has(job.dedupKey)) return;

    exported.add(job.id);
    exportedKeys.add(job.dedupKey);
    jobs.push(job);
  });

  // --- 持久化 ---
  localStorage.setItem('boss_exported_jobs', JSON.stringify([...exported]));
  localStorage.setItem('boss_exported_keys', JSON.stringify([...exportedKeys]));

  // --- 无新岗位 ---
  if (jobs.length === 0) {
    console.log('[BOSS导出] 没有新岗位。已累计 ' + exported.size + ' 条不重复记录。');
    console.log('[BOSS导出] 重置：localStorage.removeItem("boss_exported_jobs"); localStorage.removeItem("boss_exported_keys")');
    return;
  }

  // --- 生成 CSV ---
  const headers = ['岗位名称', '公司', '薪资', '地点', '标签', '链接'];
  const rows = jobs.map((j) =>
    [j.name, j.company, j.salary, j.location, j.tags, j.link]
      .map((v) => '"' + (v || '').replace(/"/g, '""') + '"')
      .join(',')
  );
  const csv = '﻿' + headers.join(',') + '\n' + rows.join('\n');

  // --- 下载 ---
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'boss_jobs_' + new Date().toISOString().slice(0, 10) + '.csv';
  a.click();
  URL.revokeObjectURL(url);

  console.log('[BOSS导出] 新增 ' + jobs.length + ' 个，累计 ' + exported.size + ' 个不重复岗位');
})();
