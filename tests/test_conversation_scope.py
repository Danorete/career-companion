"""Advice uses selected context; outward claim controls remain separate."""
from companion import context, store


def test_advice_is_not_a_verification_gate():
    assert 'Do not turn ordinary conversation into an evidence audit' in context.PLANNING_SYSTEM
    assert 'product feedback' in context.PLANNING_SYSTEM
    assert 'A saved URL is not its contents' in context.PLANNING_SYSTEM
    assert 'Every factual statement about the user' in context.DRAFT_SYSTEM
    assert 'claims' in context.DRAFT_SYSTEM


def test_selected_relationship_context_and_summary_reach_advice_only(db):
    person=store.insert(db,'items',kind='relationship',title='Example Person',
                        shareable_context='Met at a product demo; offered usability feedback.',
                        private_notes='PRIVATE_PLANNING_CANARY')
    store.insert(db,'interactions',item_id=person['id'],source='user_recap',note='Brief encounter.',
                 summary='Reviewed summary: asked to try the onboarding.',when_kind='unknown',sort_date='2026-11-13')
    _,prompt,_=context.planning_context(db,{'id':999},'Help me improve the walkthrough based on their feedback.',None,'',person['id'])
    assert 'offered usability feedback' in prompt
    assert 'asked to try the onboarding' in prompt
    assert 'PRIVATE_PLANNING_CANARY' in prompt
    outward=context.draft_context(db,'outreach','peer',[],'Say hello','',person['id'],False)
    assert 'PRIVATE_PLANNING_CANARY' not in outward.user
    assert 'asked to try the onboarding' not in outward.user
