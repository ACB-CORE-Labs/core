"""Delta Store and CRDT Event definition for GeometricDeltas.

Integrates Sopher-emitted GeometricDeltas into CORE's event-centric
reconstructive Vault/CRDT pipeline.
"""

from dataclasses import dataclass
from typing import Dict, Set, Optional

from core.abi import GeometricDelta, validate_geometric_delta

@dataclass(frozen=True)
class DeltaCRDTEvent:
    """CRDT envelope wrapping a GeometricDelta for distributed causal sync."""
    id: str                      # event hash, matches delta.id
    parents: Set[str]            # causal parents, matches delta.parents
    delta: GeometricDelta        # payload
    author: str                  # agent/compiler signature or identifier
    signature: Optional[str] = None  # optional cryptographic signature

class DeltaStore:
    """In-memory stub representing the Vault's Delta storage engine.
    
    In full implementation, this hooks into CORE's persistent SQLite/LMDB vault 
    and handles actual graph reconstruction.
    """
    def __init__(self):
        self._events: Dict[str, DeltaCRDTEvent] = {}
        # Tracks the current frontier (events with no children)
        self._frontier: Set[str] = set()

    def insert(self, delta: GeometricDelta, author: str = "unknown") -> bool:
        """Validates and inserts a GeometricDelta into the store.
        
        Args:
            delta: The GeometricDelta to insert.
            author: The identifier of the compiler/agent proposing it.
            
        Returns:
            True if inserted successfully, False if rejected by validation.
        """
        # Validate the delta against the CORE ABI contracts
        is_valid, reason = validate_geometric_delta(delta)
        if not is_valid:
            # Under reject-and-retain, we preserve state and log the failure.
            # Real implementation logs to Meta-RH and telemetry sinks.
            print(f"[REJECT-AND-RETAIN] Delta {delta.id} rejected: {reason}")
            return False

        # Create the CRDT event envelope. Copy parents: the caller may have
        # built the delta from a live frontier set, and the frontier update
        # below must never write through into the delta's causal links
        # (ADR-0026.1 §2.1).
        event = DeltaCRDTEvent(
            id=delta.id,
            parents=set(delta.parents),
            delta=delta,
            author=author
        )

        # Store the event
        self._events[event.id] = event

        # Update frontier: add new event, remove its parents from frontier
        self._frontier.add(event.id)
        self._frontier.difference_update(event.parents)

        return True

    def insert_delta(self, delta: GeometricDelta, author: str = "unknown") -> bool:
        """Alias for insert to maintain compatibility."""
        return self.insert(delta, author)

    def get_event(self, event_id: str) -> Optional[DeltaCRDTEvent]:
        """Retrieve an event by ID."""
        return self._events.get(event_id)

    @property
    def frontier(self) -> Set[str]:
        """Get a snapshot of the current causal frontier.

        Returns a copy: handing out the live set would let ``insert``'s own
        frontier maintenance mutate any delta built from it, emptying the
        frontier and severing every stored delta's parents (ADR-0026.1 §2.1).
        """
        return set(self._frontier)

    def resolve_event_frontier(self, event_ids: Set[str]) -> bool:
        """Resolves a distributed event frontier to ensure arrival-order independence.
        
        This satisfies the Delta-CRDT join-semilattice requirement that merged state
        is bit-exact regardless of the arrival order of events.
        """
        # In a full implementation, this uses `crdt.merge_kernel` over the 
        # actual event structures. Here we just verify that all events exist 
        # and are well-formed within the store.
        for eid in event_ids:
            if eid not in self._events:
                return False
        return True

