package com.dashboard.seed;

import com.dashboard.entity.*;
import com.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataSeeder implements CommandLineRunner {

    private final ProjectRepository  projectRepo;
    private final DepartmentRepository deptRepo;
    private final MemberRepository   memberRepo;
    private final IssueRepository    issueRepo;
    private final CustomPageRepository pageRepo;

    private static final Random RNG = new Random(42);

    private static final double[] MONTHLY_WEIGHTS = {
        0.8, 0.7, 1.0, 1.1, 1.2, 1.0, 0.9, 0.8, 1.1, 1.2, 1.1, 0.7
    };

    private static final String[] ISSUE_TITLES = {
        "Fix login redirect bug", "Add export to CSV feature", "Improve search performance",
        "Update API documentation", "Refactor auth middleware", "Mobile layout broken on iOS",
        "Database query optimization", "Add unit tests for payment flow", "Deploy to staging env",
        "Fix null pointer exception", "Add dark mode support", "Integrate Slack notifications",
        "Implement rate limiting", "Fix memory leak in worker", "Add pagination to list API",
        "UI component library upgrade", "Fix CORS configuration", "Improve error messages",
        "Add email verification flow", "Performance profiling report", "Fix timezone handling",
        "Add retry logic for webhooks", "Database migration script", "Fix XSS vulnerability",
        "Improve onboarding UX", "Add audit log", "Optimize image uploads",
        "Fix cache invalidation bug", "Add API versioning", "Improve test coverage",
    };

    private static final String[][] STATUSES    = {{"open","in_progress","done","closed"}, null};
    private static final int[]      STATUS_W    = {5, 10, 60, 25};
    private static final String[]   PRIORITIES  = {"low","medium","high","critical"};

    @Override
    public void run(String... args) {
        if (projectRepo.count() > 0) {
            log.info("Database already seeded, skipping.");
            return;
        }

        seedPages(seedProjects());
        log.info("✅ Seed completed.");
    }

    // ── project / dept / member data ─────────────────────────────────────────

    record ProjDef(String key, String name, String desc, String[][] depts) {}

    private static final ProjDef[] PROJECTS = {
        new ProjDef("PLATFORM", "Platform Team", "Core platform infrastructure and services", new String[][]{
            {"Backend",  "Alice Chen,Bob Wang,Carol Liu,David Zhang"},
            {"Frontend", "Eve Lin,Frank Huang,Grace Wu"},
            {"DevOps",   "Henry Chou,Iris Tsai"},
        }),
        new ProjDef("MOBILE", "Mobile App", "iOS and Android mobile application", new String[][]{
            {"iOS",     "Jack Lee,Kate Chen,Leo Yang"},
            {"Android", "Mia Wang,Nathan Liu,Olivia Ho"},
            {"QA",      "Paul Cheng,Quinn Xu"},
        }),
        new ProjDef("ANALYTICS", "Data Analytics", "Data pipeline and analytics platform", new String[][]{
            {"Data Engineering", "Rachel Sun,Sam Liao,Tina Kuo,Uma Chen"},
            {"Data Science",     "Victor Hsu,Wendy Pan,Xavier Luo"},
        }),
    };

    private Map<String, List<Member>> seedProjects() {
        Map<String, List<Member>> allMembers = new LinkedHashMap<>();

        for (ProjDef pd : PROJECTS) {
            Project project = new Project();
            project.setKey(pd.key()); project.setName(pd.name()); project.setDescription(pd.desc());
            projectRepo.save(project);

            List<Member> members = new ArrayList<>();
            for (String[] deptDef : pd.depts()) {
                Department dept = new Department();
                dept.setProject(project); dept.setName(deptDef[0]);
                deptRepo.save(dept);

                for (String mname : deptDef[1].split(",")) {
                    Member m = new Member();
                    m.setDepartment(dept);
                    m.setName(mname.trim());
                    m.setEmail(mname.trim().toLowerCase().replace(" ", ".") + "@example.com");
                    memberRepo.save(m);
                    members.add(m);
                }
            }
            allMembers.put(pd.key(), members);

            int base = switch (pd.key()) {
                case "PLATFORM" -> 18; case "MOBILE" -> 15; default -> 12;
            };

            for (int year : new int[]{2024, 2025, 2026}) {
                generateIssues(project, members, year, base);
            }
        }
        return allMembers;
    }

    private void seedPages(Map<String, List<Member>> ignored) {
        for (ProjDef pd : PROJECTS) {
            Project project = projectRepo.findByKey(pd.key()).orElseThrow();
            savePage(project, "issue-trend",        "Issue Trend",        "chart-line", 0);
            savePage(project, "member-performance", "Member Performance", "users",      1);
        }
    }

    private void savePage(Project p, String key, String name, String icon, int order) {
        CustomPage page = new CustomPage();
        page.setProject(p); page.setPageKey(key); page.setPageName(name);
        page.setIcon(icon); page.setSortOrder(order); page.setActive(true);
        pageRepo.save(page);
    }

    // ── issue generation ──────────────────────────────────────────────────────

    private void generateIssues(Project project, List<Member> members, int year, int base) {
        int counter = 1;
        List<Issue> batch = new ArrayList<>();

        for (int monthIdx = 0; monthIdx < 12; monthIdx++) {
            int month = monthIdx + 1;
            int n = Math.max(1, (int)(base * MONTHLY_WEIGHTS[monthIdx] + RNG.nextInt(7) - 3));

            LocalDateTime mStart = LocalDateTime.of(year, month, 1, 0, 0);
            LocalDateTime mEnd   = (month == 12)
                ? LocalDateTime.of(year, 12, 31, 23, 59, 59)
                : LocalDateTime.of(year, month + 1, 1, 0, 0).minusSeconds(1);

            for (int i = 0; i < n; i++) {
                Issue issue = new Issue();
                issue.setProject(project);
                issue.setIssueKey(project.getKey() + "-" + counter++);
                issue.setTitle(ISSUE_TITLES[RNG.nextInt(ISSUE_TITLES.length)]);
                issue.setPriority(PRIORITIES[RNG.nextInt(PRIORITIES.length)]);
                issue.setCreatedAt(randomBetween(mStart, mEnd));

                String status = weightedStatus();
                issue.setStatus(status);

                if (status.equals("done") || status.equals("closed")) {
                    LocalDateTime resolved = issue.getCreatedAt()
                            .plusDays(RNG.nextInt(25) + 1);
                    if (resolved.isAfter(mEnd.plusDays(30))) resolved = mEnd.plusDays(30);
                    issue.setResolvedAt(resolved);
                }

                if (!members.isEmpty()) issue.setAssignee(members.get(RNG.nextInt(members.size())));
                batch.add(issue);
            }
        }
        issueRepo.saveAll(batch);
    }

    private LocalDateTime randomBetween(LocalDateTime start, LocalDateTime end) {
        long seconds = java.time.Duration.between(start, end).getSeconds();
        return start.plusSeconds((long)(RNG.nextDouble() * seconds));
    }

    private String weightedStatus() {
        int r = RNG.nextInt(100);
        if (r < 5)  return "open";
        if (r < 15) return "in_progress";
        if (r < 75) return "done";
        return "closed";
    }
}
