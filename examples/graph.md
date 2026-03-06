```mermaid
graph TD
  subgraph SG1 [analytics]
    20250104_00_create_schema["20250104<br/>00<br/>create<br/>schema"]
    20250104_01_create_user_events["20250104<br/>01<br/>create<br/>user<br/>events"]
  end
  subgraph SG2 [auth]
    20250101_00_create_schema["20250101<br/>00<br/>create<br/>schema"]
    20250101_01_create_users["20250101<br/>01<br/>create<br/>users"]
    20250101_02_create_roles["20250101<br/>02<br/>create<br/>roles"]
    20250103_01_create_permissions["20250103<br/>01<br/>create<br/>permissions"]
  end
  subgraph SG3 [billing]
    20250102_00_create_schema["20250102<br/>00<br/>create<br/>schema"]
    20250102_01_create_plans["20250102<br/>01<br/>create<br/>plans"]
    20250102_02_create_subscriptions["20250102<br/>02<br/>create<br/>subscriptions"]
    20250102_03_seed_plans["20250102<br/>03<br/>seed<br/>plans"]:::inserterNode
  end
  subgraph SG4 [notifications]
    20250103_00_create_schema["20250103<br/>00<br/>create<br/>schema"]
    20250103_02_create_templates["20250103<br/>02<br/>create<br/>templates"]
    20250103_03_create_events["20250103<br/>03<br/>create<br/>events"]
    20250103_04_seed_templates["20250103<br/>04<br/>seed<br/>templates"]:::inserterNode
  end

  20250104_00_create_schema --> 20250104_01_create_user_events
  20250101_01_create_users --> 20250104_01_create_user_events
  20250102_02_create_subscriptions --> 20250104_01_create_user_events
  20250101_02_create_roles --> 20250103_01_create_permissions
  20250101_01_create_users --> 20250101_02_create_roles
  20250101_00_create_schema --> 20250101_01_create_users
  20250102_00_create_schema --> 20250102_01_create_plans
  20250102_01_create_plans --> 20250102_03_seed_plans
  20250101_01_create_users --> 20250102_02_create_subscriptions
  20250102_01_create_plans --> 20250102_02_create_subscriptions
  20250101_01_create_users --> 20250103_03_create_events
  20250103_02_create_templates --> 20250103_03_create_events
  20250103_00_create_schema --> 20250103_02_create_templates
  20250103_02_create_templates --> 20250103_04_seed_templates

  classDef inserterNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
  classDef schemaNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
  class 20250104_00_create_schema,20250104_01_create_user_events,20250101_00_create_schema,20250103_01_create_permissions,20250101_02_create_roles,20250101_01_create_users,20250102_00_create_schema,20250102_01_create_plans,20250102_02_create_subscriptions,20250103_00_create_schema,20250103_03_create_events,20250103_02_create_templates schemaNode```