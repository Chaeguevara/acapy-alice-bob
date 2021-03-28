"""Abstract base class for linked data proofs."""


from abc import ABC
from pyld import jsonld
from typing import List, TYPE_CHECKING, Union

from typing_extensions import TypedDict

from ..constants import SECURITY_CONTEXT_URL
from ..error import LinkedDataProofException
from ..document_loader import DocumentLoader
from ..validation_result import ProofResult

# ProofPurpose and LinkedDataProof depend on each other
if TYPE_CHECKING:
    from ..purposes.ProofPurpose import ProofPurpose


class DeriveProofResult(TypedDict):
    """Result dict for deriving a proof."""

    document: dict
    proof: Union[dict, List[dict]]


class LinkedDataProof(ABC):
    """Base Linked data proof."""

    def __init__(
        self,
        *,
        signature_type: str,
        proof: dict = None,
        supported_derive_proof_types: Union[List[str], None] = None,
    ):
        """Initialize new LinkedDataProof instance."""
        self.signature_type = signature_type
        self.proof = proof
        self.supported_derive_proof_types = supported_derive_proof_types

    async def create_proof(
        self,
        *,
        document: dict,
        purpose: "ProofPurpose",
        document_loader: DocumentLoader,
    ) -> dict:
        """Create proof for document.

        Args:
            document (dict): The document to create the proof for
            purpose (ProofPurpose): The proof purpose to include in the proof
            document_loader (DocumentLoader): Document loader used for resolving

        Returns:
            dict: The proof object

        """
        raise LinkedDataProofException(
            f"{self.signature_type} signature suite does not support creating proofs"
        )

    async def verify_proof(
        self,
        *,
        proof: dict,
        document: dict,
        purpose: "ProofPurpose",
        document_loader: DocumentLoader,
    ) -> ProofResult:
        """Verify proof against document and proof purpose.

        Args:
            proof (dict): The proof to verify
            document (dict): The document to verify the proof against
            purpose (ProofPurpose): The proof purpose to verify the proof against
            document_loader (DocumentLoader): Document loader used for resolving

        Returns:
            ValidationResult: The results of the proof verification

        """
        raise LinkedDataProofException(
            f"{self.signature_type} signature suite does not support verifying proofs"
        )

    async def derive_proof(
        self,
        *,
        proof: dict,
        document: dict,
        reveal_document: dict,
        document_loader: DocumentLoader,
        nonce: bytes = None,
    ) -> DeriveProofResult:
        """Derive proof for document, returning derived document and proof.

        Args:
            proof (dict): The proof to derive from
            document (dict): The document to derive the proof for
            reveal_document (dict): The JSON-LD frame the revealed attributes
            document_loader (DocumentLoader): Document loader used for resolving
            nonce (bytes, optional): Nonce to use for the proof. Defaults to None.

        Returns:
            DeriveProofResult: The derived document and proof

        """
        raise LinkedDataProofException(
            f"{self.signature_type} signature suite does not support deriving proofs"
        )

    def _get_verification_method(
        self, *, proof: dict, document_loader: DocumentLoader
    ) -> dict:
        """Get verification method for proof."""

        verification_method = proof.get("verificationMethod")

        if isinstance(verification_method, dict):
            verification_method: str = verification_method.get("id")

        if not verification_method:
            raise LinkedDataProofException('No "verificationMethod" found in proof')

        # TODO: This should optionally use the context of the document?
        framed = jsonld.frame(
            verification_method,
            frame={
                "@context": SECURITY_CONTEXT_URL,
                "@embed": "@always",
                "id": verification_method,
            },
            options={
                "documentLoader": document_loader,
                "expandContext": SECURITY_CONTEXT_URL,
                # if we don't set base explicitly it will remove the base in returned
                # document (e.g. use key:z... instead of did:key:z...)
                # same as compactToRelative in jsonld.js
                "base": None,
            },
        )

        if not framed:
            raise LinkedDataProofException(
                f"Verification method {verification_method} not found"
            )

        if framed.get("revoked"):
            raise LinkedDataProofException("The verification method has been revoked.")

        return framed

    def match_proof(self, signature_type: str) -> bool:
        """Match signature type to signature type of this suite."""
        return signature_type == self.signature_type
