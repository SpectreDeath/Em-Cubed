% ==============================================================================
%  skill_taxonomy.pl — Declarative Ontology for Em-Cubed Skill Framework
% ==============================================================================
%  Single source of truth for professional taxonomy, reference materials,
%  subskill dependency trees, and inference rules.
%
%  Query surface:
%    ?- profession_domain(data_scientist, Domain).
%    ?- domain_reference(statistics, Ref).
%    ?- belongs_to_profession(skill_name, Profession).
%    ?- recommend_materials(data_scientist, Ref).
%    ?- requires_meta_wrapper(skill_id, meta_wrapper).
%    ?- has_subskill(parent, child).
%    ?- resolve_skill_ancestry(leaf, Ancestry).
%    ?- infer_professions_from_keywords([stochastic, markov], Professions).
%    ?- get_profession_hierarchy(Profession, [Domains, MetaWrappers, Skills]).
%    ?- get_domain_skills(Domain, Skills).
% ==============================================================================

:- module(skill_taxonomy, [
    profession_domain/2,
    domain_reference/2,
    belongs_to_profession/2,
    requires_meta_wrapper/2,
    has_subskill/2,
    requires_reference/2,
    meta_wraps/1,
    child_skill/1,
    recommend_materials/2,
    resolve_skill_ancestry/2,
    infer_professions_from_keywords/2,
    skill_is/2,
    skill_belongs_to/2,
    skill_requires/2,
    get_profession_hierarchy/2,
    get_domain_skills/2
]).

:- use_module(library(lists)).
:- use_module(library(apply)).

% ============================================================
%  1. PROFESSION-DOMAIN TAXONOMY (many-to-many)
% ============================================================

profession_domain(data_scientist,           statistics).
profession_domain(data_scientist,           stochastic_processes).
profession_domain(data_scientist,           optimization).

profession_domain(medical_entomologist,     epidemiology).
profession_domain(medical_entomologist,     stochastic_processes).

profession_domain(software_engineer,        distributed_systems).
profession_domain(software_engineer,        general_tooling).

profession_domain(epidemiologist,           epidemiology).

profession_domain(statistician,             statistics).

profession_domain(quantitative_analyst,     technical_analysis).
profession_domain(quantitative_analyst,     statistics).
profession_domain(quantitative_analyst,     time_series).

profession_domain(financial_modeler,        technical_analysis).
profession_domain(financial_modeler,        risk_modeling).

profession_domain(ml_researcher,            machine_learning).
profession_domain(ml_researcher,            ensemble_methods).
profession_domain(ml_researcher,            feature_engineering).
profession_domain(ml_researcher,            model_validation).

profession_domain(nlp_engineer,             nlp).

profession_domain(operations_researcher,    optimization).
profession_domain(operations_researcher,    resource_management).

profession_domain(clinical_researcher,      clinical_trials).
profession_domain(clinical_researcher,      statistics).

profession_domain(biostatistician,          clinical_trials).
profession_domain(biostatistician,          statistics).

profession_domain(forensic_economist,       forensic_economics).

profession_domain(research_scientist,       knowledge_graph).
profession_domain(research_scientist,       simulation).

% ============================================================
%  2. AUTHORITY REFERENCE GROUNDING
% ============================================================

domain_reference(statistics,
    "Wackerly - Mathematical Statistics with Applications").
domain_reference(statistics,
    "Ross - Introduction to Probability Models").

domain_reference(stochastic_processes,
    "Ross - Introduction to Probability Models").
domain_reference(stochastic_processes,
    "Norris - Markov Chains").

domain_reference(optimization,
    "Nocedal & Wright - Numerical Optimization").
domain_reference(optimization,
    "Glover & Laguna - Tabu Search").
domain_reference(optimization,
    "de Jong - Analysis of Behavior of a Class of Genetic Adaptive Systems").

domain_reference(machine_learning,
    "Hastie, Tibshirani & Friedman - The Elements of Statistical Learning").
domain_reference(machine_learning,
    "Bishop - Pattern Recognition and Machine Learning").
domain_reference(machine_learning,
    "Sutton & Barto - Reinforcement Learning: An Introduction").
domain_reference(machine_learning,
    "Goodfellow et al. - Deep Learning").

domain_reference(distributed_systems,
    "Lamport - Time, Clocks, and the Ordering of Events").
domain_reference(distributed_systems,
    "Kleppmann - Designing Data-Intensive Applications").
domain_reference(distributed_systems,
    "Vazirani - Verifiability in WebAssembly").
domain_reference(distributed_systems,
    "OASIS - SAML 2.0 / OpenID Connect Core Specification").

domain_reference(epidemiology,
    "Keeling & Rohani - Modeling Infectious Diseases in Humans and Animals").

domain_reference(clinical_trials,
    "ICH E9 - Statistical Principles for Clinical Trials").
domain_reference(clinical_trials,
    "FDA 21 CFR 50 - Informed Consent").
domain_reference(clinical_trials,
    "FDA 21 CFR 312 - IND Safety Reporting").
domain_reference(clinical_trials,
    "MedDRA / CTCAE - Adverse Event Severity Grading Hierarchies").

domain_reference(forensic_economics,
    "Fisher & Waters - Regression Analysis with IBM SPSS").

domain_reference(technical_analysis,
    "Murphy - Technical Analysis of the Financial Markets").
domain_reference(technical_analysis,
    "Hurst et al. - A Big Jump in the Market (ARFIMA origins)").

domain_reference(time_series,
    "Brockwell & Davis - Time Series: Theory and Methods").

domain_reference(nlp,
    "Manning & Schütze - Foundations of Statistical NLP").

domain_reference(knowledge_graph,
    "Hogan et al. - Knowledge Graphs (ACM Computing Surveys)").

domain_reference(simulation,
    "Law & Kelton - Simulation Modeling and Analysis").

domain_reference(ensemble_methods,
    "Kuhn & Johnson - Applied Predictive Modeling").
domain_reference(model_validation,
    "Kuhn & Johnson - Applied Predictive Modeling").

domain_reference(resource_management,
    "Hillier & Lieberman - Introduction to Operations Research").

domain_reference(feature_engineering,
    "Kuhn & Johnson - Feature Engineering and Selection").

domain_reference(ml_operations,
    "Sculley et al. - Machine Learning: The High-Interest Credit Card of Technical Debt").

domain_reference(general_tooling,
    "Abelson & Sussman - Structure and Interpretation of Computer Programs").
domain_reference(general_tooling,
    "Microsoft LSP 3.17 - Language Server Protocol Specification").

% ============================================================
%  3. SUBSKILL DEPENDENCY TREES
% ============================================================

% --- STATISTICS
has_subskill(calculating_descriptive_stats, calculate_central_tendency).
has_subskill(calculating_descriptive_stats, calculate_dispersion).
has_subskill(assert_test_constraints, evaluate_p_value).
has_subskill(assert_test_constraints, execute_chi_square_independence).
has_subskill(calculate_mean_confidence_interval, evaluate_p_value).

% --- STOCHASTIC_PROCESSES
has_subskill(modelling_stochastic_processes, evaluate_stationarity).
has_subskill(modelling_stochastic_processes, generate_transition_matrix).
has_subskill(modelling_stochastic_processes, execute_monte_carlo_walk).
has_subskill(modelling_stochastic_processes, calculate_pagerank_vector).
has_subskill(modelling_stochastic_processes, compile_simulation_histogram).
has_subskill(modelling_stochastic_processes, formulate_ngram_model).
has_subskill(modelling_stochastic_processes, assert_context_gate).

% --- OPTIMIZATION
has_subskill(running_optimizers, cma_es_optimizer).
has_subskill(running_optimizers, differential_evolution_solver).
has_subskill(running_optimizers, central_force_optimization).
has_subskill(running_optimizers, chaos_optimization).
has_subskill(running_optimizers, dialectic_search).
has_subskill(running_optimizers, fractal_based_algorithm).
has_subskill(running_optimizers, anarchic_society_optimization).
has_subskill(running_optimizers, stochastic_diffusion_search).
has_subskill(running_optimizers, spiral_dynamics_optimization).
has_subskill(running_optimizers, monte_carlo_simulator).

% --- MACHINE_LEARNING
has_subskill(building_classifiers, logistic_regression_classifier).
has_subskill(building_classifiers, svm_classifier).
has_subskill(building_classifiers, naive_bayes_classifier).
has_subskill(building_classifiers, decision_tree_splits).
has_subskill(building_classifiers, random_forest_ensemble).
has_subskill(building_classifiers, reinforcement_learning_agent).
has_subskill(building_graph_models, graph_neural_network).

% --- META_SKILLS
has_subskill(running_specialized_optimizers, z3_schedule_solver).
has_subskill(running_specialized_optimizers, pathfinding_with_constraints).

% --- DISTRIBUTED_SYSTEMS
has_subskill(building_distributed_infrastructure, dag_task_scheduler).
has_subskill(building_distributed_infrastructure, durable_execution_engine).
has_subskill(building_distributed_infrastructure, wasm_execution_sandbox).
has_subskill(building_distributed_infrastructure, observability_dashboard).
has_subskill(building_distributed_infrastructure, forecasting_monitor).
has_subskill(building_distributed_infrastructure, multi_agent_coordinator).

% --- CLINICAL_TRIALS
has_subskill(managing_clinical_trials, icf_clause_validator).
has_subskill(managing_clinical_trials, sae_reporting_threshold_tester).
has_subskill(managing_clinical_trials, sap_endpoint_consistency_checker).
has_subskill(managing_clinical_trials, non_inferiority_margin_checker).
has_subskill(managing_clinical_trials, dmc_counting_rule_analyzer).
has_subskill(managing_clinical_trials, ae_severity_tree_evaluator).

% --- EPIDEMIOLOGY
has_subskill(modelling_epidemiological_spread, stochastic_transmission_network).
has_subskill(modelling_epidemiological_spread, gradient_descent_optimizer).

% --- NLP
has_subskill(processing_natural_language, js_text_transformer).
has_subskill(processing_natural_language, sentiment_intelligence_engine).
has_subskill(processing_natural_language, natural_language_generator).
has_subskill(processing_natural_language, test_rag_pipeline).

% --- TIME_SERIES
has_subskill(analysing_time_series, time_series_preprocessor).
has_subskill(analysing_time_series, autoregressive_parameter_estimator).
has_subskill(analysing_time_series, time_series_forecaster).

% --- ANALYTICS
has_subskill(performing_analytics, pagerank_centrality).
has_subskill(performing_analytics, markov_chain_sequence).
has_subskill(performing_analytics, bayesian_evidence_updater).
has_subskill(performing_analytics, statistical_test_advisor).

% --- DECISION_MAKING
has_subskill(supporting_decisions, multi_surface_decision_tree).
has_subskill(supporting_decisions, multi_criteria_weight_calculator).
has_subskill(supporting_decisions, strategic_planner).
has_subskill(supporting_decisions, test_decision_maker).

% --- DATA_PROCESSING
has_subskill(processing_data, time_series_preprocessor).
has_subskill(processing_data, sql_aggregator).
has_subskill(processing_data, data_pipeline_orchestrator).

% --- KNOWLEDGE_GRAPH
has_subskill(building_knowledge_graphs, knowledge_graph_builder).

% --- RESOURCE_MANAGEMENT
has_subskill(planning_resources, resource_allocation_planner).
has_subskill(planning_resources, predictive_capacity_planner).

% --- FEATURE_ENGINEERING
has_subskill(engineering_features, feature_engineering_pipeline).

% --- MODEL_VALIDATION
has_subskill(validating_models, model_validation_suite).

% --- ML_OPERATIONS
has_subskill(monitoring_ml_ops, anomaly_detection_system).

% --- ENSEMBLE
has_subskill(managing_ensembles, ensemble_method_manager).

% --- SIMULATION
has_subskill(building_simulations, system_dynamics_modeler).

% --- FORENSIC_ECONOMICS
has_subskill(performing_forensic_analysis, linear_regression).

% --- TECHNICAL_ANALYSIS
has_subskill(analysing_markets, candlestick_pattern_analyzer).
has_subskill(analysing_markets, arfima_gph_estimator).
has_subskill(analysing_markets, falling_risk_pyramid).
has_subskill(analysing_markets, pyramid_risk_verifier).

% --- RECOMMENDER_SYSTEMS
has_subskill(building_recommenders, recommendation_engine).

% --- AUTOMATION
has_subskill(automating_workflows, workflow_synthesiser).
has_subskill(automating_workflows, github_pr_manager).

% --- LLM_PROCESSING
has_subskill(processing_llm_workflows, advanced_llm_processor).

% --- GRAPH_ML
has_subskill(building_graph_ml, graph_neural_network).

% --- EXAMPLES
has_subskill(example_pipelines, python_prolog_pipeline).
has_subskill(example_pipelines, sqlite_pipeline).

% --- TESTING
has_subskill(testing_skills, z3_test_skill).

% --- META_SKILLS
has_subskill(meta_skill_functions, prompt_quality_evaluator).

% --- GENERAL_TOOLING
has_subskill(building_general_tools, python_calculator).
has_subskill(building_general_tools, integrated_logic_solver).
has_subskill(building_general_tools, prolog_logic_solver).
has_subskill(building_general_tools, hy_fuzzy_logic).
has_subskill(building_general_tools, intelligent_task_planner).
has_subskill(building_general_tools, constraint_satisfaction_solver).

% ============================================================
%  4. META-WRAPPER (GUARDRAIL / SUPERVISORY) RELATIONS
% ============================================================

requires_meta_wrapper(evaluate_p_value,                    assert_test_constraints).
requires_meta_wrapper(execute_chi_square_independence,     assert_test_constraints).
requires_meta_wrapper(calculate_central_tendency,          validate_measurement_level).
requires_meta_wrapper(calculate_dispersion,                validate_measurement_level).
requires_meta_wrapper(k_means_clustering,                  sap_endpoint_consistency_checker).
requires_meta_wrapper(durable_execution_engine,            dag_task_scheduler).
requires_meta_wrapper(time_series_forecaster,              forecasting_monitor).
requires_meta_wrapper(logistic_regression_classifier,      z3_bound_verifier).
requires_meta_wrapper(svm_classifier,                      z3_bound_verifier).
requires_meta_wrapper(non_inferiority_margin_checker,      z3_bound_verifier).
requires_meta_wrapper(sae_reporting_threshold_tester,      z3_bound_verifier).
requires_meta_wrapper(informed_consent_form_clause_validator, z3_bound_verifier).
requires_meta_wrapper(autoregressive_parameter_estimator,  quality_pipeline_monitor).
requires_meta_wrapper(naive_bayes_classifier,              quality_pipeline_monitor).
requires_meta_wrapper(predictive_capacity_planner,         resource_allocation_planner).
requires_meta_wrapper(bayesian_evidence_updater,           prolog_topology_validator).
requires_meta_wrapper(sqlite_pipeline,                     datalog_inspector).
requires_meta_wrapper(dmc_counting_rule_analyzer,          clingo_boundary_verifier).
requires_meta_wrapper(ensemble_method_manager,             hy_fuzzy_weighting).
requires_meta_wrapper(feature_engineering_pipeline,        hy_fuzzy_scoring).
requires_meta_wrapper(multi_surface_decision_tree,         kanren_rule_validator).
requires_meta_wrapper(wasm_execution_sandbox,              container_executor).

% ============================================================
%  5. SKILL-TO-PROFESSION DIRECT MAPPING
% ============================================================

% STATISTICS
belongs_to_profession(calculate_central_tendency,            statistician).
belongs_to_profession(calculate_dispersion,                  statistician).
belongs_to_profession(evaluate_p_value,                      statistician).
belongs_to_profession(execute_chi_square_independence,       statistician).
belongs_to_profession(calculate_mean_confidence_interval,    statistician).
belongs_to_profession(validate_measurement_level,            statistician).
belongs_to_profession(assert_test_constraints,               statistician).
belongs_to_profession(calculate_correlation_profile,         statistician).
belongs_to_profession(fit_linear_regression,                 statistician).
belongs_to_profession(autoregressive_parameter_estimator,    statistician).
belongs_to_profession(naive_bayes_classifier,                statistician).
belongs_to_profession(statistical_bootstrap_analyzer,        statistician).
belongs_to_profession(uncertainty_quantifier,                statistician).

% STOCHASTIC_PROCESSES
belongs_to_profession(evaluate_stationarity,                 data_scientist).
belongs_to_profession(generate_transition_matrix,            data_scientist).
belongs_to_profession(execute_monte_carlo_walk,              data_scientist).
belongs_to_profession(calculate_pagerank_vector,             data_scientist).
belongs_to_profession(compile_simulation_histogram,          data_scientist).
belongs_to_profession(n_gram_token_predictor,                data_scientist).
belongs_to_profession(assert_context_gate,                   data_scientist).

% OPTIMIZATION
belongs_to_profession(cma_es_optimizer,                     operations_researcher).
belongs_to_profession(differential_evolution_solver,         operations_researcher).
belongs_to_profession(central_force_optimization,            operations_researcher).
belongs_to_profession(chaos_optimization,                    operations_researcher).
belongs_to_profession(dialectic_search,                      operations_researcher).
belongs_to_profession(fractal_based_algorithm,               operations_researcher).
belongs_to_profession(anarchic_society_optimization,         operations_researcher).
belongs_to_profession(stochastic_diffusion_search,           operations_researcher).
belongs_to_profession(spiral_dynamics_optimization,          operations_researcher).
belongs_to_profession(monte_carlo_simulator,                 research_scientist).
belongs_to_profession(z3_schedule_solver,                    operations_researcher).
belongs_to_profession(pathfinding_with_constraints,          operations_researcher).

% MACHINE_LEARNING
belongs_to_profession(logistic_regression_classifier,       ml_researcher).
belongs_to_profession(svm_classifier,                       ml_researcher).
belongs_to_profession(decision_tree_splits,                  ml_researcher).
belongs_to_profession(random_forest_ensemble,                ml_researcher).
belongs_to_profession(reinforcement_learning_agent,          ml_researcher).
belongs_to_profession(graph_neural_network,                  ml_researcher).
belongs_to_profession(ensemble_method_manager,               ml_researcher).

% NLP
belongs_to_profession(js_text_transformer,                  nlp_engineer).
belongs_to_profession(sentiment_intelligence_engine,        nlp_engineer).
belongs_to_profession(natural_language_generator,           nlp_engineer).
belongs_to_profession(test_rag_pipeline,                    nlp_engineer).

% DISTRIBUTED_SYSTEMS
belongs_to_profession(dag_task_scheduler,                   software_engineer).
belongs_to_profession(durable_execution_engine,             software_engineer).
belongs_to_profession(wasm_execution_sandbox,               software_engineer).
belongs_to_profession(observability_dashboard,              software_engineer).
belongs_to_profession(forecasting_monitor,                  software_engineer).
belongs_to_profession(multi_agent_coordinator,              software_engineer).

% CLINICAL_TRIALS
belongs_to_profession(icf_clause_validator,                 clinical_researcher).
belongs_to_profession(sae_reporting_threshold_tester,       clinical_researcher).
belongs_to_profession(sap_endpoint_consistency_checker,     clinical_researcher).
belongs_to_profession(non_inferiority_margin_checker,       biostatistician).
belongs_to_profession(dmc_counting_rule_analyzer,           clinical_researcher).
belongs_to_profession(ae_severity_tree_evaluator,           clinical_researcher).
belongs_to_profession(k_means_clustering,                   biostatistician).

% EPIDEMIOLOGY
belongs_to_profession(stochastic_transmission_network,      epidemiologist).
belongs_to_profession(gradient_descent_optimizer,           epidemiologist).

% FORENSIC_ECONOMICS
belongs_to_profession(linear_regression,                    forensic_economist).

% TECHNICAL_ANALYSIS
belongs_to_profession(candlestick_pattern_analyzer,         quantitative_analyst).
belongs_to_profession(arfima_gph_estimator,                 quantitative_analyst).
belongs_to_profession(falling_risk_pyramid,                 quantitative_analyst).
belongs_to_profession(pyramid_risk_verifier,                quantitative_analyst).

% TIME_SERIES
belongs_to_profession(time_series_preprocessor,             statistician).
belongs_to_profession(time_series_forecaster,               statistician).

% ANALYTICS
belongs_to_profession(pagerank_centrality,                  data_scientist).
belongs_to_profession(markov_chain_sequence,                data_scientist).
belongs_to_profession(bayesian_evidence_updater,            data_scientist).
belongs_to_profession(statistical_test_advisor,             statistician).

% DECISION_MAKING
belongs_to_profession(multi_surface_decision_tree,          data_scientist).
belongs_to_profession(multi_criteria_weight_calculator,     data_scientist).
belongs_to_profession(strategic_planner,                    data_scientist).
belongs_to_profession(test_decision_maker,                  data_scientist).

% KNOWLEDGE_GRAPH
belongs_to_profession(knowledge_graph_builder,              research_scientist).

% RESOURCE_MANAGEMENT
belongs_to_profession(resource_allocation_planner,          operations_researcher).
belongs_to_profession(predictive_capacity_planner,          operations_researcher).

% FEATURE_ENGINEERING
belongs_to_profession(feature_engineering_pipeline,         ml_researcher).

% MODEL_VALIDATION
belongs_to_profession(model_validation_suite,               ml_researcher).

% ML_OPERATIONS
belongs_to_profession(anomaly_detection_system,             ml_researcher).

% ENSEMBLE
belongs_to_profession(ensemble_method_manager,              ml_researcher).

% SIMULATION
belongs_to_profession(system_dynamics_modeler,              research_scientist).

% RECOMMENDER_SYSTEMS
belongs_to_profession(recommendation_engine,                data_scientist).

% AUTOMATION
belongs_to_profession(workflow_synthesiser,                 software_engineer).
belongs_to_profession(github_pr_manager,                    software_engineer).

% LLM_PROCESSING
belongs_to_profession(advanced_llm_processor,               nlp_engineer).

% EXAMPLES
belongs_to_profession(python_prolog_pipeline,               software_engineer).
belongs_to_profession(sqlite_pipeline,                      data_scientist).

% TESTING
belongs_to_profession(z3_test_skill,                        software_engineer).

% META_SKILLS
belongs_to_profession(prompt_quality_evaluator,             ml_researcher).

% GENERAL_TOOLING
belongs_to_profession(python_calculator,                    software_engineer).
belongs_to_profession(integrated_logic_solver,              software_engineer).
belongs_to_profession(prolog_logic_solver,                  software_engineer).
belongs_to_profession(hy_fuzzy_logic,                       data_scientist).
belongs_to_profession(intelligent_task_planner,             software_engineer).
belongs_to_profession(constraint_satisfaction_solver,       operations_researcher).

% ============================================================
%  6. DERIVED / CONVENIENCE PREDICATES
% ============================================================

skill_is(evaluate_stationarity,             procedural).
skill_is(generate_transition_matrix,        procedural).
skill_is(execute_monte_carlo_walk,         procedural).
skill_is(calculate_pagerank_vector,        procedural).
skill_is(compile_simulation_histogram,     procedural).
skill_is(n_gram_token_predictor,           procedural).
skill_is(assert_context_gate,              procedural).
skill_is(cma_es_optimizer,                 numerical).
skill_is(differential_evolution_solver,    numerical).
skill_is(central_force_optimization,       numerical).
skill_is(chaos_optimization,               numerical).
skill_is(dialectic_search,                 numerical).
skill_is(fractal_based_algorithm,          numerical).
skill_is(anarchic_society_optimization,    numerical).
skill_is(stochastic_diffusion_search,      numerical).
skill_is(spiral_dynamics_optimization,     numerical).
skill_is(z3_schedule_solver,               symbolic).
skill_is(pathfinding_with_constraints,     symbolic).

child_skill(Child) :- has_subskill(_, Child).
meta_wraps(MetaWrapper) :- requires_meta_wrapper(_, MetaWrapper).

% ============================================================
%  7. INFERENCE PREDICATES  (Public API for Python engine)
% ============================================================

% recommend_materials(+Profession, -Reference)
recommend_materials(Profession, Reference) :-
    profession_domain(Profession, Domain),
    domain_reference(Domain, Reference).

% resolve_skill_ancestry(+Skill, -Ancestry)
resolve_skill_ancestry(Skill, Ancestry) :-
    belongs_to_profession(Skill, Profession),
    profession_domain(Profession, Domain),
    (   has_subskill(Parent, Skill)
    ->  Ancestry = ancestry(Skill, Profession, Domain, Parent)
    ;   Ancestry = ancestry(Skill, Profession, Domain, root)
    ).

% infer_professions_from_keywords(+KeywordList, -ProfessionList)
infer_professions_from_keywords(KeywordList, ProfessionList) :-
    findall(P,
        ( member(Keyword, KeywordList),
          profession_matches_keyword(Keyword, P) ),
        RawList),
    sort(RawList, ProfessionList).

profession_matches_keyword(Keyword, data_scientist) :-
    member(Keyword, [data, science, statistics, stochastic, model, ml,
                     machine_learning, regression, classification,
                     bayesian, inference]).
profession_matches_keyword(Keyword, medical_entomologist) :-
    member(Keyword, [entomology, insect, vector, mosquito, habitat,
                     incidence, field_surveillance]).
profession_matches_keyword(Keyword, software_engineer) :-
    member(Keyword, [software, engineering, distributed, system,
                     api, lsp, wasm, compile, deploy, orchestrate]).
profession_matches_keyword(Keyword, statistician) :-
    member(Keyword, [statistician, hypothesis, p_value, confidence_interval,
                     chi_square, anova, test, sampling, distribution]).
profession_matches_keyword(Keyword, operations_researcher) :-
    member(Keyword, [optimize, scheduling, resource, allocation, lp,
                     constraint, evolutionary, optimizer, search,
                     operations, research, logistics, queuing,
                     inventory, network_flow]).
profession_matches_keyword(Keyword, clinical_researcher) :-
    member(Keyword, [clinical, trial, endpoint, dmc, sae, icf,
                     non_inferiority, ctcae, meddra]).
profession_matches_keyword(Keyword, biostatistician) :-
    member(Keyword, [biostatistics, survival, kaplan_meier, biostat]).
profession_matches_keyword(Keyword, epidemiologist) :-
    member(Keyword, [epidemiology, infectious, seir, disease,
                     transmission, outbreak]).
profession_matches_keyword(Keyword, ml_researcher) :-
    member(Keyword, [neural, deep_learning, gnn, transformer,
                     reinforcement, q_learning, random_forest,
                     decision_tree, svm, ensemble]).
profession_matches_keyword(Keyword, nlp_engineer) :-
    member(Keyword, [nlp, language, sentiment, text, token,
                     ngram, rag, embedding, llm]).
profession_matches_keyword(Keyword, quantitative_analyst) :-
    member(Keyword, [quantitative, trading, candlestick, arfima,
                     hurst, technical, market, forensics]).
profession_matches_keyword(Keyword, financial_modeler) :-
    member(Keyword, [financial, derivative, pricing, portfolio,
                     risk, valuation, actuary]).
profession_matches_keyword(Keyword, forensic_economist) :-
    member(Keyword, [forensic, damages, earnings, counterfactual,
                     econometric, regression]).
profession_matches_keyword(Keyword, research_scientist) :-
    member(Keyword, [research, science, simulation, knowledge_graph,
                     markov, monte_carlo, discovery]).

% get_profession_hierarchy(+Profession, -[Domains, MetaWrappers, Skills])
get_profession_hierarchy(Profession, [Domains, MetaWrappers, Skills]) :-
    findall(D, profession_domain(Profession, D), Domains),
    findall(M, requires_meta_wrapper(_, M), MetaWrappers),
    findall(S, belongs_to_profession(S, Profession), Skills).

% get_domain_skills(+Domain, -Skills)
get_domain_skills(Domain, Skills) :-
    findall(Skill,
        ( profession_domain(Profession, Domain),
          belongs_to_profession(Skill, Profession) ),
        Skills).
