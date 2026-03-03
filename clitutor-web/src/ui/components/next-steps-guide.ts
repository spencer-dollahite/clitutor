import type { LessonData } from "../../core/models";

type Platform = "windows" | "macos" | "linux" | "chromebook";
type SetupPath = "local-native" | "local-vm" | "cloud";
type CloudProvider = "aws" | "gcp" | "azure" | "digitalocean";

interface PlanSection {
  title: string;
  details: string;
  commands?: string[];
}

interface SetupPlan {
  headline: string;
  summary: string;
  sections: PlanSection[];
}

export class NextStepsGuide {
  private host: HTMLElement;
  private lesson: LessonData;
  private root: HTMLElement;
  private platform: Platform;
  private path: SetupPath = "local-native";
  private provider: CloudProvider = "gcp";

  constructor(parent: HTMLElement, lesson: LessonData) {
    this.host = parent;
    this.lesson = lesson;
    this.platform = this.detectPlatform();
    this.root = document.createElement("div");
    this.root.className = "next-steps-guide";
    this.host.appendChild(this.root);
    this.render();
  }

  destroy(): void {
    this.root.remove();
  }

  private render(): void {
    const plan = this.buildPlan();
    const showCloudProviders = this.path === "cloud";

    this.root.innerHTML = `
      <section class="next-hero">
        <p class="next-kicker">Final Lesson</p>
        <h1>${this.escapeHtml(this.lesson.title)}</h1>
        <p class="next-hero-copy">
          No browser VM for this final module. Build your real Linux setup and
          follow a personalized plan based on your system.
        </p>
      </section>

      <section class="next-grid">
        <article class="next-panel">
          <h2>1. Pick Your System</h2>
          <div class="next-choice-row" data-choice="platform">
            ${this.choiceButton("platform", "windows", "Windows", this.platform === "windows")}
            ${this.choiceButton("platform", "macos", "macOS", this.platform === "macos")}
            ${this.choiceButton("platform", "linux", "Linux", this.platform === "linux")}
            ${this.choiceButton("platform", "chromebook", "Chromebook", this.platform === "chromebook")}
          </div>
        </article>

        <article class="next-panel">
          <h2>2. Pick Your Environment</h2>
          <div class="next-choice-row" data-choice="path">
            ${this.choiceButton("path", "local-native", "Local Native", this.path === "local-native")}
            ${this.choiceButton("path", "local-vm", "Local VM", this.path === "local-vm")}
            ${this.choiceButton("path", "cloud", "Cloud VM", this.path === "cloud")}
          </div>
          ${showCloudProviders ? `
            <p class="next-inline-label">Cloud provider:</p>
            <div class="next-choice-row compact" data-choice="provider">
              ${this.choiceButton("provider", "gcp", "GCP", this.provider === "gcp")}
              ${this.choiceButton("provider", "aws", "AWS", this.provider === "aws")}
              ${this.choiceButton("provider", "azure", "Azure", this.provider === "azure")}
              ${this.choiceButton("provider", "digitalocean", "DigitalOcean", this.provider === "digitalocean")}
            </div>
          ` : ""}
        </article>
      </section>

      <section class="next-plan">
        <div class="next-plan-head">
          <h2>${this.escapeHtml(plan.headline)}</h2>
          <p>${this.escapeHtml(plan.summary)}</p>
        </div>
        <ol class="next-step-list">
          ${plan.sections.map((section, idx) => `
            <li class="next-step-item">
              <div class="next-step-index">${idx + 1}</div>
              <div class="next-step-content">
                <h3>${this.escapeHtml(section.title)}</h3>
                <p>${this.escapeHtml(section.details)}</p>
                ${section.commands && section.commands.length > 0 ? `
                  <pre><code>${this.escapeHtml(section.commands.join("\n"))}</code></pre>
                  <button class="next-copy-btn" data-copy="${this.escapeAttr(section.commands.join("\n"))}">
                    Copy Commands
                  </button>
                ` : ""}
              </div>
            </li>
          `).join("")}
        </ol>
      </section>

      <section class="next-grid">
        <article class="next-panel">
          <h2>What You Just Learned</h2>
          <ul>
            <li>Linux navigation, files, and permissions</li>
            <li>Text processing, scripting, and shell productivity</li>
            <li>Networking, SSH, Git, vim, tmux, and dotfiles</li>
            <li>Foundational security tooling and troubleshooting</li>
          </ul>
        </article>
        <article class="next-panel">
          <h2>Recommended Next Topics</h2>
          <ul>
            <li>Package management (<code>apt</code>, <code>dnf</code>, or <code>pacman</code>)</li>
            <li>Service management with <code>systemd</code></li>
            <li>Docker and container workflows</li>
            <li>Automation with Ansible and Terraform</li>
          </ul>
        </article>
      </section>

      <section class="next-panel next-resources">
        <h2>High-Value Free Resources</h2>
        <div class="next-resource-grid">
          <a href="https://overthewire.org/wargames/bandit/" target="_blank" rel="noreferrer">OverTheWire: Bandit</a>
          <a href="https://linuxjourney.com/" target="_blank" rel="noreferrer">Linux Journey</a>
          <a href="https://linuxcommand.org/" target="_blank" rel="noreferrer">The Linux Command Line</a>
          <a href="https://docs.docker.com/get-started/" target="_blank" rel="noreferrer">Docker Getting Started</a>
          <a href="https://docs.ansible.com/ansible/latest/getting_started/" target="_blank" rel="noreferrer">Ansible Getting Started</a>
        </div>
      </section>
    `;

    this.bindEvents();
  }

  private bindEvents(): void {
    this.root.querySelectorAll<HTMLElement>("[data-choice-value]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const type = btn.dataset.choiceType;
        const value = btn.dataset.choiceValue;
        if (!type || !value) return;

        if (type === "platform") this.platform = value as Platform;
        if (type === "path") this.path = value as SetupPath;
        if (type === "provider") this.provider = value as CloudProvider;

        this.render();
      });
    });

    this.root.querySelectorAll<HTMLElement>(".next-copy-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const text = btn.dataset.copy ?? "";
        if (!text) return;
        try {
          await navigator.clipboard.writeText(text);
          btn.textContent = "Copied";
          setTimeout(() => { btn.textContent = "Copy Commands"; }, 1000);
        } catch {
          btn.textContent = "Copy Failed";
          setTimeout(() => { btn.textContent = "Copy Commands"; }, 1200);
        }
      });
    });
  }

  private buildPlan(): SetupPlan {
    if (this.path === "cloud") {
      return this.cloudPlan();
    }
    if (this.path === "local-vm") {
      return this.localVmPlan();
    }
    return this.localNativePlan();
  }

  private localNativePlan(): SetupPlan {
    if (this.platform === "windows") {
      return {
        headline: "Windows + WSL2 (Recommended)",
        summary: "Fast setup with real Linux kernel integration on Windows 10/11.",
        sections: [
          {
            title: "Install WSL2",
            details: "Run PowerShell as Administrator and install Ubuntu with one command.",
            commands: ["wsl --install"],
          },
          {
            title: "Initialize your Linux user",
            details: "Reboot if prompted, open Ubuntu, create your Linux username/password, then update packages.",
            commands: ["sudo apt update && sudo apt upgrade -y"],
          },
          {
            title: "Install your daily tooling",
            details: "Add Git, curl, vim, tmux, and build utilities so your environment matches this course.",
            commands: ["sudo apt install -y git curl vim tmux build-essential"],
          },
        ],
      };
    }

    if (this.platform === "macos") {
      return {
        headline: "macOS + Native Unix Shell",
        summary: "Use Terminal/iTerm and install GNU/Linux-compatible tooling with Homebrew.",
        sections: [
          {
            title: "Install Homebrew",
            details: "Homebrew gives macOS package management similar to Linux workflows.",
            commands: ['/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'],
          },
          {
            title: "Install CLI essentials",
            details: "Install Git, tmux, and modern GNU tools for parity with Linux tutorials.",
            commands: ["brew install git tmux coreutils gnu-sed grep"],
          },
          {
            title: "Create your working directories",
            details: "Set up a clean workspace and verify your shell profile.",
            commands: ["mkdir -p ~/dev ~/scripts", "echo 'export PATH=\"/opt/homebrew/bin:$PATH\"' >> ~/.zprofile"],
          },
        ],
      };
    }

    if (this.platform === "chromebook") {
      return {
        headline: "Chromebook + Linux Development Environment",
        summary: "Use the built-in Debian container for real shell access and package management.",
        sections: [
          {
            title: "Enable Linux in ChromeOS settings",
            details: "Open Settings -> Advanced -> Developers -> Linux development environment.",
          },
          {
            title: "Update and install essentials",
            details: "Open Terminal from the app launcher and install your baseline tools.",
            commands: ["sudo apt update && sudo apt upgrade -y", "sudo apt install -y git curl vim tmux"],
          },
          {
            title: "Verify environment",
            details: "Confirm Linux is active and your tools are available.",
            commands: ["uname -a", "git --version", "tmux -V"],
          },
        ],
      };
    }

    return {
      headline: "Linux + Native Setup",
      summary: "Start directly on your installed distribution with a clean dev baseline.",
      sections: [
        {
          title: "Update your system",
          details: "Use your distro package manager to refresh package metadata and upgrades.",
          commands: [
            "sudo apt update && sudo apt upgrade -y    # Debian/Ubuntu",
            "sudo dnf upgrade --refresh -y             # Fedora",
          ],
        },
        {
          title: "Install core command-line tools",
          details: "Ensure Git, curl, vim, tmux, and SSH clients are installed.",
          commands: ["sudo apt install -y git curl vim tmux openssh-client"],
        },
        {
          title: "Set up your workspace",
          details: "Create folders for repositories and scripts, then initialize dotfiles.",
          commands: ["mkdir -p ~/dev ~/scripts ~/.config", "touch ~/.bashrc ~/.gitconfig"],
        },
      ],
    };
  }

  private localVmPlan(): SetupPlan {
    const host =
      this.platform === "macos"
        ? "UTM or Multipass"
        : this.platform === "windows"
          ? "VirtualBox or VMware"
          : "VirtualBox or GNOME Boxes";

    return {
      headline: `${this.platformLabel()} + Local VM`,
      summary: `Run Ubuntu Server in ${host} for a reproducible Linux sandbox.`,
      sections: [
        {
          title: "Install a VM manager",
          details: "Choose a lightweight hypervisor and verify virtualization support is enabled.",
        },
        {
          title: "Create Ubuntu 22.04 LTS VM",
          details: "Use 2 CPU cores, 2-4 GB RAM, 20+ GB disk, and bridged or NAT networking.",
        },
        {
          title: "Bootstrap the VM",
          details: "Install baseline packages and create a non-root user for daily work.",
          commands: [
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y git curl vim tmux build-essential",
            "id && uname -a",
          ],
        },
      ],
    };
  }

  private cloudPlan(): SetupPlan {
    const providerLabel = this.provider === "gcp"
      ? "Google Cloud"
      : this.provider === "aws"
        ? "AWS"
        : this.provider === "azure"
          ? "Azure"
          : "DigitalOcean";

    const providerStep: PlanSection =
      this.provider === "gcp"
        ? {
            title: "Create an e2-micro Ubuntu VM",
            details: "Use the always-free eligible machine type and allow SSH access.",
            commands: ["gcloud compute instances list"],
          }
        : this.provider === "aws"
          ? {
              title: "Launch a free-tier EC2 Ubuntu instance",
              details: "Use t2.micro/t3.micro, attach SSH key pair, and open port 22 from your IP.",
              commands: ["aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId'"],
            }
          : this.provider === "azure"
            ? {
                title: "Create a B1s Ubuntu VM",
                details: "Provision via portal or CLI and enable SSH key authentication.",
                commands: ["az vm list -d -o table"],
              }
            : {
                title: "Create a basic Ubuntu droplet",
                details: "Use the lowest-cost shared CPU option and add your SSH key on creation.",
              };

    return {
      headline: `${this.platformLabel()} + Cloud (${providerLabel})`,
      summary: "Best for production-like networking, remote access, and infrastructure skills.",
      sections: [
        {
          title: "Create account and billing guardrails",
          details: "Enable budget alerts before provisioning so there are no cost surprises.",
        },
        providerStep,
        {
          title: "SSH in and configure your baseline",
          details: "After first login, update packages and install your core CLI toolkit.",
          commands: [
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y git curl vim tmux",
          ],
        },
      ],
    };
  }

  private choiceButton(
    type: "platform" | "path" | "provider",
    value: string,
    label: string,
    selected: boolean,
  ): string {
    return `
      <button class="next-choice-btn${selected ? " selected" : ""}"
              data-choice-type="${type}"
              data-choice-value="${value}">
        ${label}
      </button>
    `;
  }

  private platformLabel(): string {
    if (this.platform === "windows") return "Windows";
    if (this.platform === "macos") return "macOS";
    if (this.platform === "chromebook") return "Chromebook";
    return "Linux";
  }

  private detectPlatform(): Platform {
    const platform = navigator.platform.toLowerCase();
    if (platform.includes("win")) return "windows";
    if (platform.includes("mac")) return "macos";
    if (platform.includes("linux")) return "linux";
    return "linux";
  }

  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  private escapeAttr(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
}
