using System.Collections.Generic;

namespace RungProof.Next.Workspace;

public enum WorkspaceArrangeOperation
{
    AlignX,
    AlignY,
    AlignZ,
    DistributeX,
    DistributeY,
    DistributeZ,
}

public sealed record WorkspaceDocument(
    int Version,
    string SourceSceneId,
    IReadOnlyList<WorkspacePlacement> Placements,
    IReadOnlyList<WorkspaceConnectorLink>? ConnectorLinks = null,
    IReadOnlyList<WorkspaceSignalLink>? SignalLinks = null,
    IReadOnlyList<WorkspaceGroup>? Groups = null
);

public sealed record WorkspacePlacement(
    string InstanceId,
    string AssetId,
    double[] Position,
    double[] Rotation,
    double[] Scale
);

public sealed record WorkspaceConnectorLink(
    string Id,
    string FromInstanceId,
    string FromConnectorId,
    string ToInstanceId,
    string ToConnectorId
);

public sealed record WorkspaceSignalLink(
    string Id,
    string InstanceId,
    string SignalId,
    string PointName
);

public sealed record WorkspaceGroup(
    string Id,
    string Name,
    IReadOnlyList<string> MemberInstanceIds,
    double[]? Pivot = null,
    string? ParentGroupId = null
);
