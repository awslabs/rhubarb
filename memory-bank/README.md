# Rhubarb Memory Bank

This Memory Bank provides comprehensive context for the Rhubarb project, enabling effective development across sessions.

## Memory Bank Structure

### Core Files (Required Reading)
1. **`projectbrief.md`** - Project overview, requirements, and goals
2. **`productContext.md`** - User experience goals and target personas  
3. **`systemPatterns.md`** - Architecture patterns and design decisions
4. **`techContext.md`** - Technology stack and development setup
5. **`activeContext.md`** - Current work focus and recent discoveries
6. **`progress.md`** - What works vs what needs development

### File Relationships
```
projectbrief.md (foundation)
├── productContext.md (why & how)
├── systemPatterns.md (architecture)  
├── techContext.md (technology)
├── activeContext.md (current state)
└── progress.md (status & roadmap)
```

## Quick Start for New Sessions

### For Development Tasks
1. Read `activeContext.md` for current work focus
2. Check `progress.md` for what's working vs what needs work
3. Reference `systemPatterns.md` for architectural guidance
4. Use `techContext.md` for setup and configuration details

### For Planning Tasks
1. Start with `projectbrief.md` for project scope
2. Review `productContext.md` for user goals
3. Check `progress.md` for current priorities
4. Reference `activeContext.md` for recent insights

## Key Project Facts

- **Current Version**: 0.0.6 (published on PyPI as `pyrhubarb`)
- **Primary Classes**: `DocAnalysis` and `DocClassification`
- **Technology**: Python >=3.11, Pydantic v2, Amazon Bedrock
- **Current Branch**: xlsx-support (adding Excel/PowerPoint support)
- **Architecture**: Multi-modal document processing with AWS integration

## Recent Context (As of Memory Bank Creation)

- **Status**: Stable core functionality with active development
- **Focus**: File format expansion (Excel, PowerPoint, CSV, WebP, EML)
- **Strengths**: Comprehensive document analysis, sliding window processing, AWS native
- **Priorities**: Performance optimization, error handling, user experience improvements

## Memory Bank Maintenance

This Memory Bank should be updated when:
- Significant architectural changes occur
- New features are implemented
- User feedback changes priorities
- Development focus shifts
- Technical debt is addressed

Update `activeContext.md` most frequently, followed by `progress.md` for status changes.
