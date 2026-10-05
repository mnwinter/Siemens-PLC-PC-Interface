using System;
using System.Linq;
using Godot;
using RungProof.Next.Catalog;

namespace RungProof.Next.Scenes;

public static partial class SceneComposer
{
    private static void ConfigureCncTendingStock(Node3D root, SceneDefinition scene)
    {
        var machine = root.GetNode<Node3D>("cnc_machine");
        var load = root.GetNode<Node3D>("cnc_workpiece");
        var stock = machine.FindChild("WORK_stock", true, false) as MeshInstance3D
            ?? throw new InvalidOperationException("CNC tending installation requires the delivered WORK_stock.");
        var definition = scene.Equipment.Single(equipment => equipment.Id == "cnc_workpiece");
        var size = NumberArray(definition.Config, "size", new[] { 0.4, 0.14, 0.252 });
        // Move the actual billet into the scene's addressable load root. The
        // machine's vise stays installed; it must never travel on the belt.
        var bounds = stock.Transform * stock.GetAabb();
        var basis = Basis.FromScale(new Vector3((float)size[0], (float)size[1], (float)size[2]) / bounds.Size) * stock.Basis;
        stock.Owner = null;
        stock.GetParent().RemoveChild(stock);
        load.AddChild(stock);
        stock.Transform = new Transform3D(basis,
            new Vector3(0, (float)size[1] / 2, 0) - basis * stock.GetAabb().GetCenter());

        // The delivered jaws' inner faces are Z=.489/.741. A seated billet
        // uses their center Z=.615 and Y=1.66 bottom. Fill the visible 195 mm
        // gap from the existing vise base to that bearing plane with a shoe.
        var viseBase = (MeshInstance3D)machine.FindChild("WORK_vise_base", true, false);
        AddBox(machine, new Vector3(0.42f, 0.195f, 0.252f),
            new Vector3(0, 1.5625f, 0.615f), viseBase.GetActiveMaterial(0)).Name = "WORK_stock_bearing_shoe";
    }
}
