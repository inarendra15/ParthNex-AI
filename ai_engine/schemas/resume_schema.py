from dataclasses import dataclass, field


@dataclass
class ResumeProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


@dataclass
class ResumeData:

    profile: ResumeProfile

    skills: list = field(default_factory=list)

    education: list = field(default_factory=list)

    experience: list = field(default_factory=list)

    projects: list = field(default_factory=list)