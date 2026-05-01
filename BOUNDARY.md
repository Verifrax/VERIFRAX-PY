
# VERIFRAX-PY Boundary

VERIFRAX-PY may inspect, verify, fetch, explain, and refuse.

VERIFRAX-PY may not decide truth.

## May

* expose a Python SDK
* expose a CLI
* query public machine-contract surfaces
* inspect local bundles
* verify supported local object bundles
* explain missing object-chain links
* refuse unsupported claims
* inspect package metadata
* expose source-boundary bindings
* declare PyPI custody requirements

## May not

* define constitutional law
* define accepted state
* issue authority
* execute governed actions
* publish proof as proof.verifrax.net
* replace VERIFRAX-verify
* recognize terminal truth
* assign terminal recourse
* rewrite current truth
* impersonate a sovereign chamber
* treat package publication as legitimacy
  EOF

cat > governance/REPO_ADMISSION.json <<'EOF'
{
"schema": "verifrax.repo-admission.v1",
"status": "ACTIVE_BOUNDARY",
"repo": "Verifrax/VERIFRAX-PY",
"class": "implementation-package-python-boundary",
"primary_role": "python-sdk-cli-interface",
"sovereign_chamber": false,
"truth_owner": false,
"host_default": false,
"package_default": true,
"distribution_surfaces": {
"pypi": "verifrax"
},
"source_authority": {
"authored_protocol": "Verifrax/VERIFRAX",
"api_contract": "Verifrax/VERIFRAX-API",
"public_verifier": "Verifrax/VERIFRAX-verify"
},
"may_verify": true,
"may_fetch_projected_objects": true,
"may_explain_refusal": true,
"may_issue_authority": false,
"may_execute_governed_actions": false,
"may_publish_proof": false,
"may_recognize_terminal_truth": false,
"may_assign_recourse": false
}
